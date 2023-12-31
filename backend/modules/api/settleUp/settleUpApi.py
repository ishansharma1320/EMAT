from flask import Blueprint, jsonify, request,current_app

from modules.models.User import User
from modules.models.Group import Group
from modules.models.SettleUp import SettleUp
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import ValidationError, OperationError
import traceback
import json
from modules.utils.utilFunctions import send_email
import datetime

settleUp = Blueprint('settleUp', __name__)

# get user profile
@settleUp.route("", methods=["GET"])
@jwt_required()
def who_owes_what():
    """
    Gets the Settlement information for a user with respect to other users (who owes what) for a group
    
    Returns:
        A python dictionary containing status & a response key-value pair on a successful response
    """
    result = {"status": False}
    user_id_verified = get_jwt_identity()
    group_id = request.args.get("group_id")
    pipeline = [{ "$unwind": "$expenses" }, { "$group": { "_id": "$expenses.spent_by", "total": { "$sum": "$expenses.amount" } } }]
    if group_id:
        try:
            pipeline.insert(0,{ "$match": { "group_id": group_id } })
            # runs an aggregate pipeline that unwinds the expenses sub array as root and
            # then for each spent_by (user_id) key all expense amounts are summed
            group_stats = Group.objects.aggregate(*pipeline)
            group_stats_json = [dict(doc) for doc in group_stats]
            group_data = Group.objects.get_or_404(group_id=group_id)
            participants = group_data.participants
            user_names = User.objects.filter(user_id__in=participants)
            user_names = [json.loads(x.to_json()) for x in user_names]
            # filter the aggregation result, on what is spent by the user that makes the API call and other users
            user_spent = [x for x in group_stats_json if x["_id"] == user_id_verified]
            other_spent = [x for x in group_stats_json if x["_id"] != user_id_verified]
            other_participants = [x for x in participants if x != user_id_verified]
            
            # ensures that all users have a total sum of expenses object
            for user in other_participants:
                other_spent_obj = next(filter(lambda item: item['_id'] == user, other_spent), None)
                if other_spent_obj is None:
                    other_spent.append({"_id":user,"total": 0})

            print(group_stats_json)
            if len(user_spent) > 0:
                user_spent = user_spent[0]
            else:
                user_spent  = {"user_id": user_id_verified, "total": 0}

            # calculates the owing
            for other_expense in other_spent:
                other_expense["total"] = (user_spent["total"]/len(participants)) - (other_expense["total"]/len(participants))
            
            # when some users have settled up 
            # removes the settle up amount for all other users
            user_object = User.objects.get_or_404(user_id=user_id_verified)
            for expense in other_spent:
                expense_user_id = expense['_id']
                settled_up_expense_objs = user_object.settleUp.filter(user_id=expense_user_id,group_id=group_id)
                for settled_up_expense_object in settled_up_expense_objs:
                    expense["total"] -= settled_up_expense_object['amount']

            
            for expense in other_spent:
                user_object = next(filter(lambda x: x['user_id'] == expense['_id'],user_names),None)
                expense['user_name'] = f"{user_object['first_name']} {user_object['last_name']}"

            result["status"] = True
            result["response"] = other_spent
        except Exception as e:
            traceback_message = traceback.format_exc()
            print(traceback_message)
            result['error'] = f"{e.__class__.__name__} occured"
            result['traceback'] = traceback_message
    else:
        result["response"] = "Incomplete Query Parameters: 'group_id'"
    
    return result

@settleUp.route("/notify",methods=["POST"])
@jwt_required()
def notify():
    """
    Sends the notification via email intimating all the users in the request body for sending back the money
    
    Returns:
        A python dictionary containing status & a response key-value pair on a successful response
    """
    result = {"status": False}
    content_type = request.headers.get('Content-Type')
    user_id_verified = get_jwt_identity()
    json_data = request.json
    print(json_data)
    if content_type == current_app.config["JSON-CONTENT-TYPE"]:
        try:
            user = User.objects.get_or_404(user_id=user_id_verified)
            group_id = json_data.get("group_id",None)
            notify_users = json_data.get("notify_users",[])
            if group_id is not None and len(notify_users) > 0:
                group = Group.objects.get_or_404(group_id=group_id)
                group = json.loads(group.to_json())
                notify_user_ids = [x["user_id"] for x in notify_users]
                notify_user_objects = User.objects.filter(user_id__in=notify_user_ids)
                # sends the email for notification
                mail_object = {'subject': 'EMAT - Notify User for payment'}
                for notify_user_obj in notify_user_objects:
                    notify_user_obj = json.loads(notify_user_obj.to_json())
                    index = notify_user_ids.index(notify_user_obj.get("user_id"))
                    obj = notify_users[index]
                    mail_object["message"] = f'You owe amount {obj.get("amount","undefined")} {notify_user_obj.get("currency","undefined")} to {user.first_name} in {group.get("group_name","undefined")}'
                    send_email(mail_object,notify_user_obj.get("email"))
            
            result["status"] = True
            result["response"] = "Users notified"
        except Exception as e:
            traceback_message = traceback.format_exc()
            print(traceback_message)
            result['error'] = f"{e.__class__.__name__} occured"
            result['traceback'] = traceback_message

        else:
            if group_id is None:
                result["response"] = "Group ID (group_id) not set in request body"
            elif len(notify_users) == 0:
                result["response"] = "Notify User Array (notify_users) cannot be empty in request body"
            
                
    else:
        result["response"] = f"Unsupported Content-Type: {content_type}"

    return result


@settleUp.route("/settle",methods=['POST'])
@jwt_required()
def settle():
    """
    Allow users to settle among themselves
    
    Returns:
        A python dictionary containing status & a response key-value pair on a successful response
    """
    result = {"status": False}
    content_type = request.headers.get('Content-Type')
    user_id_verified = get_jwt_identity()
    if content_type == current_app.config["JSON-CONTENT-TYPE"]:
        required_fields = ['group_id','user_id','amount','last_settled_at']
        json_data = request.json
        print(json_data)
        for transaction in json_data.get('transactions',[]):
            if set(required_fields) == set(list(transaction.keys())):
                user_id_settling = transaction.get('user_id')
                group_id = transaction.get('group_id')
                last_settled_at_as_string = transaction.get('last_settled_at')
                amount = transaction.get('amount')
                last_settled_at = datetime.datetime.strptime(last_settled_at_as_string, "%Y-%m-%dT%H:%M:%S.%fZ")
                user_settling = User.objects.get_or_404(user_id=user_id_settling)
                user_called_settled = User.objects.get_or_404(user_id=user_id_verified)
                # settle Up sub documents are saved for both the users (settler & settling)
                try:            
                    settling_object = SettleUp(user_id=user_id_verified,group_id=group_id,last_settled_at=last_settled_at,amount=0-amount,settling=True)
                    user_settling.settleUp.append(settling_object)

                    called_settle_object = SettleUp(user_id=user_id_settling,group_id=group_id,last_settled_at=last_settled_at,amount=amount,settler=True)
                    user_called_settled.settleUp.append(called_settle_object)

                    user_settling.save()
                    user_called_settled.save()
                    result['status'] = True
                    result['response'] = f'{user_id_verified} and {user_id_settling} settled up'
                except Exception as e:
                    traceback_message = traceback.format_exc()
                    print(traceback_message)
                    result['error'] = f"{e.__class__.__name__} occured"
                    result['traceback'] = traceback_message
               
            else:
                json_body_keys_list = list(transaction.keys())
                unavailable_keys = [x for x in required_fields if x not in json_body_keys_list]
                error_message = []
                for key in unavailable_keys:
                    error_message.append(f'{key} does not exist in request body')
                
                error_msg_as_string = ', '.join(error_message)
                result['response'] = f'Incomplete JSON body: {error_msg_as_string}'
        
    else:
        result["response"] = f"Unsupported Content-Type: {content_type}"
    
    return result


            
