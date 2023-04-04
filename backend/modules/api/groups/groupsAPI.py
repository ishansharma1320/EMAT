from flask import Blueprint,request,abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.models.Group import Group
from modules.models.User import User
from modules.utils.utilFunctions import createObjectWithRequiredFields,generate_verification_code,sendEmail
import json
import traceback


group = Blueprint('group',__name__)

@group.route("/register",methods=['POST'])
@jwt_required()
def registerGroup():
    content_type = request.headers.get('Content-Type')
    user_id_verified = get_jwt_identity()
    result = {"status": False}
    status = None
    if content_type == 'application/json':
        if user_id_verified:
            try:
                json_data = request.json
                required_fields = ['group_name','group_currency']
                participants = json_data.get("participants",None)
                group = Group()
                joiningToken = generate_verification_code()
                description = json_data.get("group_description",None)
                group.created_by = user_id_verified
                group.joiningToken = joiningToken
                if description is not None:
                    group.group_description = description
                
                if participants is not None:
                    users = User.objects.filter(email__in=participants)
                    users = [json.loads(x.to_json()) for x in users]
                    emails_registered = [x['email'] for x in users if x.get('email') is not None]
                    email_not_registered = [x for x in participants if x not in emails_registered]
                    created_user_object = next(filter(lambda item: item['user_id'] == user_id_verified, users), None)
                    if created_user_object is not None:
                        created_email = created_user_object.get("email",None)
                        if created_email is not None:
                            registered_email_object = {"subject": f"{created_email} invited you to {json_data.get('group_name','Group')} on EMAT","message":f"Group Verification Code: {joiningToken}"}
                            for email in emails_registered:                    
                                sendEmail(registered_email_object,email)
                            
                            for email in email_not_registered:
                                sendEmail(registered_email_object,email)
                        
                    participants = [x['user_id'] for x in users if x.get('user_id') is not None]
                    participants.append(user_id_verified)
                    participants = list(set(participants))
                    group.participants = participants
                
                result = createObjectWithRequiredFields(group,required_fields,json_data,result) 
                status = 201
            except Exception as e:
                traceback_message = traceback.format_exc()
                print(traceback_message)
                result['error'] = f"{e.__class__.__name__} occured"
                result['traceback'] = traceback_message
                status = 500
            
    else:
        result["error"] = "Unsupported Content-Type in headers"
        status = 415
    return result,status

@group.route("/list",methods=['GET'])
@jwt_required()
def listGroups():
    result = {"status": True}
    user_id_verified = get_jwt_identity()
    status = None

    if user_id_verified:
        try:
            groups = Group.objects.filter(participants__in=[user_id_verified])
            groups = [json.loads(group.to_json()) for group in groups]
            result["response"] = groups
            status = 200
           

        except Exception as e:
            traceback_message = traceback.format_exc()
            print(traceback_message)
            result['error'] = f"{e.__class__.__name__} occured"
            result['traceback'] = traceback_message
            status = 500
       
    
    return result,status
        

@group.route("/delete",methods=['POST'])
@jwt_required()
def deleteGroup():
    content_type = request.headers.get('Content-Type')
    user_id_verified = get_jwt_identity()

    result = {"status": False}
    status = None
    
    if content_type == 'application/json':
        
        if user_id_verified:
            try:
                json_data = request.json
                group_id = json_data.get('group_id',None)
                if group_id is not None:
                    group = Group.objects.filter(group_id=group_id)
                    group.delete()
                    result["status"] = True
                    result["response"] = f"{group_id} Deleted"
                    status = 200
                else:
                    result["error"] = "Group ID cannot be null in request body"
                    status = 400
            except Exception as e:
                traceback_message = traceback.format_exc()
                print(traceback_message)
                result['error'] = f"{e.__class__.__name__} occured"
                result['traceback'] = traceback_message
                status = 500          
    else:
        result["error"] = "Unsupported Content-Type in headers"
        status = 415
    return result,status

@group.route("/update",methods=['PUT'])
@jwt_required()
def updateGroup():
    content_type = request.headers.get('Content-Type')
    user_id_verified = get_jwt_identity()
    result = {"status": False}
    status = None
    if content_type == 'application/json':
        if user_id_verified:
            try:
                json_data = request.json
                required_key = 'group_id'
                json_keys = list(json_data.keys())
                if required_key in json_keys:
                    group_id = json_data[required_key]
                    group = Group.objects.get_or_404(group_id=group_id)
                    keys_to_update = [x for x in json_keys if x != required_key]
                    for key in keys_to_update:
                        group[key] = json_data[key]
                    
                    group.save()
                    result["status"] = True
                    result["response"] = f"Group {group_id} updated"
                    status = 200
                else:
                    result["error"] = "Group ID cannot be null in request body" 
                    status = 400
            except Exception as e:
                traceback_message = traceback.format_exc()
                print(traceback_message)
                result['error'] = f"{e.__class__.__name__} occured"
                result['traceback'] = traceback_message
                status = 500   
    else:
        result["error"] = "Unsupported Content-Type in headers"
        status = 415
    
    return result,status

@group.route("/stats",methods=['GET'])
@jwt_required()
def getGroupStats():
    result = {"status": False}
    group_id = request.args.get("group_id")
    pipeline = [{ "$unwind": "$expenses" }, { "$group": { "_id": "$expenses.spent_by", "total": { "$sum": "$expenses.amount" } } }]
    if group_id:
        try:
            pipeline.insert(0,{ "$match": { "group_id": group_id } })
            group_stats = Group.aggregate(*pipeline)
            group_stats_json = [x.to_json() for x in group_stats]
            user_ids = [x["_id"] for x in group_stats_json]
            result["status"] = True
            if len(user_ids) > 0:
                users = User.objects.filter(user_id__in=user_ids)
                keys_needed = ['first_name','last_name','email']
                for user in users:
                    index = user_ids.index(user.user_id)
                    for key in keys_needed:
                        group_stats_json[index][key] = user[key]
                
                group_data = Group.objects.get_or_404(group_id=group_id)
                participants = group_data.participants
                amounts_owed_all = []
                total_expense = sum([x["total"] for x in group_stats_json])
                number_participants = len(participants)
                for user in participants:
                    amount_owed = {}
                    amount_owed["_id"] = user
                    amount_owed["owed"] =  0 - (total_expense/number_participants)
                    if user in user_ids:
                        index = user_ids.index(user.user_id)
                        amount_owed["owed"] += group_stats_json[index]["total"] 
                          
                result["response"] = {"max":max(group_stats_json,key=lambda x: x["total"]),"min":min(amounts_owed_all,key=lambda x: x["owed"])}
            else:
                result["response"] = f"No Expenses in group: {group_id}"
        except Exception as e:
            traceback_message = traceback.format_exc()
            print(traceback_message)
            result['error'] = f"{e.__class__.__name__} occured"
            result['traceback'] = traceback_message
    else:
        result["response"] = f"Incomplete Query Parameters: 'group_id' is missing"

    return result
            
@group.route("/join-group",methods=['GET'])
@jwt_required()
def joinGroup():
    user_id_verified = get_jwt_identity()
    result = {"status": False}
    verification_token = request.args.get("verification_code")

    if user_id_verified:
        if verification_token is not None:
            try:
                group_array = Group.objects.filter(joiningToken=verification_token)
                if not group:
                    abort(404)
                else:
                    group = group_array[0]
                    if user_id_verified not in group.participants:
                        group.participants.append(user_id_verified)
                        group.save()
                    else:
                        print(f"User Exists: {user_id_verified} in {group.participants}")
                    
                    result['status'] = True
                    result['response'] = f'User {user_id_verified} has joined group {group.name}'
            except Exception as e:
                traceback_message = traceback.format_exc()
                print(traceback_message)
                result['error'] = f"{e.__class__.__name__} occured"
                result['traceback'] = traceback_message

        else:
            result['status'] = False
            result['response'] = "Verification Token: verification_code should be set in query parameters"
    
    return result
