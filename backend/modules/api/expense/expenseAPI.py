from flask import Blueprint,request
from modules.models.Group import Group
from modules.models.Expense import Expense
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback
import json

expense = Blueprint('expense',__name__)

@expense.route('/detail',methods=['GET'])
@jwt_required()
def detailExpense():
    result = {"status": False}
    user_id_verified = get_jwt_identity()
    # print(dict(request.headers))
    status = None
        
    if user_id_verified:
        expense_id = request.args.get("expense_id",None)
        group_id = request.args.get("group_id",None)
        try:
            if expense_id is not None and group_id is not None:
                
                    group = Group.objects.get_or_404(group_id = group_id)
                    print(expense_id)
                    expense = group.expenses.get(expense_id = expense_id)
                    result['status'] = True
                    if expense:
                        result['response'] = expense.to_json()
                        status = 200
                    else:
                        result['response'] = f"Expense with ID {expense_id} does not exist"
                        status = 404
                
            else:
                if expense_id is None:
                    result['error'] = f"Expense ID cannot be null in the request params"

                if group_id is None:
                    result['error'] = f"Group ID cannot be null in the request params"
                status = 400
        except Exception as e:
            traceback_message = traceback.format_exc()
            print(traceback_message)
            result['error'] = f"{e.__class__.__name__} occured"
            result['traceback'] = traceback_message
            status = 500
       
    
    return result,status
        

@expense.route('/create',methods=['POST'])
@jwt_required()
def createExpense():
    content_type = request.headers.get('Content-Type')
    user_id_verified = get_jwt_identity()
    result = {"status": False}
    status = None
    
    if content_type == 'application/json':
     
        if user_id_verified:
            try:
                json_data = request.json
                required_fields = ['group_id','email','amount']
                json_keys = list(json_data.keys())
                required_fields_exist = set(required_fields).issubset(json_keys)

                if required_fields_exist:
                    group_id = json_data['group_id']
                    group = Group.objects.get_or_404(group_id=group_id)
                    groups_dict = json.loads(group.to_json())
                    email = json_data['email']
                    if email in groups_dict['participants']:
                        amount = json_data['amount']
                        expense = Expense(group_id=group_id,spent_by=email,amount=amount)
                        if 'description' in json_keys:
                            expense.description = json_data['description']
                        group.expenses.append(expense)
                        group.save()
                        result['status'] = True
                        expense_id = json.loads(expense.to_json())['expense_id']
                        result['response'] = f'Expense {expense_id} Created'
                        status = 201
                    else:
                        result['error']= f'Email ID {email} does not exist as a participant in Group {group_id}'
                        status = 404
                else:
                    fields_not_exist = [i for i in required_fields if i not in json_keys]
                    fields_ne_string = ", ".join(fields_not_exist)
                    result['error'] = f'Fields: {fields_ne_string} not in request'
                    status = 400

            except Exception as e:
                traceback_message = traceback.format_exc()
                print(traceback_message)
                result['error'] = f"{e.__class__.__name__} occured"
                result['traceback'] = traceback_message
                status = 500
           
    else:
        result['error'] = f'Unsupported Header Content-Type {content_type}'
        status = 415
    return result,status

@expense.route('/update',methods=['PUT'])
@jwt_required()
def updateExpense():
    content_type = request.headers.get('Content-Type')
    user_id_verified = get_jwt_identity()
    result = {"status": False}
    status = None
    if content_type == 'application/json':
        if user_id_verified:
            try:
                json_data = request.json
                updatable_fields = ['description']
                required_fields = ['expense_id','group_id']
                json_keys = list(json_data.keys())
                required_fields_exist = set(required_fields).issubset(json_keys)
                if required_fields_exist:
                    group_id = json_data['group_id']
                    expense_id = json_data['expense_id']
                    group = Group.objects.get_or_404(group_id=group_id)
                    expense = group.expenses.get(expense_id=expense_id)
                    updatable_fields_exist = set(updatable_fields).issubset(json_keys)
                    if updatable_fields_exist:
                        for key in updatable_fields:
                            expense[key] = json_data[key]
                        group.save()
                        result['status'] = True
                        result['response'] = f"Expense: {expense_id} updated"
                        status = 200
                    else:
                        updatable_fields_string = ", ".join(updatable_fields)
                        result['error'] = f"Only fields: {updatable_fields_string} can be updated"
                        status = 400
                else:
                    fields_not_exist = [i for i in required_fields if i not in json_keys]
                    fields_ne_string = ", ".join(fields_not_exist)
                    result['error'] = f'Fields: {fields_ne_string} not in request'
                    status = 400
            except Exception as e:
                traceback_message = traceback.format_exc()
                print(traceback_message)
                result['error'] = f"{e.__class__.__name__} occured"
                result['traceback'] = traceback_message
                status = 500
       
    else:
        result['error'] = f'Unsupported Header Content-Type {content_type}'
        status = 415

    return result,status