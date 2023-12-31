from flask import Blueprint, jsonify, request, current_app

from modules.models.User import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import ValidationError, OperationError
import traceback

profile = Blueprint('profile', __name__)

# get user profile
@profile.route("/user", methods=["GET"])
@jwt_required()
def get_profile():
    """
    Gets the user Profile (user object) from mongoDB
    
    Returns:
        A python dictionary containing status & a message key-value pair on a successful response
    """

    try:

        user_id = get_jwt_identity()
        user = User.objects.get_or_404(user_id = user_id)
        if not user:
            return jsonify({"status": False, "error": "the user does not exist"}), 404
    
        return jsonify({"status": True, "message": user}), 200
    
    except OperationError as e:
        return jsonify({"status": False, "error": str(e)}), 401
    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500


@profile.route("/update", methods=["PUT"])
@jwt_required()
def update_user():
    """
    Updates the user profile (user object) and stores the updated values to mongoDB
    
    Returns:
        A python dictionary containing status & a response key-value pair on a successful response
    """
    content_type = request.headers.get('Content-Type')
    user_id_verified = get_jwt_identity()
    result = {"status": False}
    if content_type == current_app.config["JSON-CONTENT-TYPE"]:
        if user_id_verified:
            try:
                user = User.objects.get_or_404(user_id = user_id_verified)
                # following fields are updatable
                updatable_fields = ['first_name','last_name','currency','monthly_budget_amount','warning_budget_amount']
                json_data = request.json
                json_list_keys = list(json_data.keys())

                # filters all keys that are present in updatable_fields and in the request body
                keys_to_update = [x for x in json_list_keys if x in updatable_fields]

                for key in keys_to_update:
                    user[key] = json_data[key]
                
                user.save()
                result['status'] = True
                result['response'] = f"User Details for {user_id_verified} updated"
            except Exception as e:
                traceback_message = traceback.format_exc()
                print(traceback_message)
                result['error'] = f"{e.__class__.__name__} occured"
                result['traceback'] = traceback_message
        else:
            result['response'] = 'User session Expired'
    else:
        result['response'] = f'Unsupported Content Type in Headers: {content_type} Supported: "application/json"'

    return result


# delete user
@profile.route("/delete_user")
@jwt_required()
def delete_user():
    """
    Deletes the user profile (user object) from mongoDB
    
    Returns:
        A python dictionary containing status & a message key-value pair on a successful response
    """
    try:
        user = User.objects(user_id=get_jwt_identity())

        if not user:
            return jsonify({"status": False, "error": "the user does not exist"}), 401


        user.delete()
        return jsonify({"status": True, "message": "the user has been deleted successfully"}), 200
    
    except ValidationError as e:
        return jsonify({"status": False, "error": str(e)}), 403
    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500


@profile.route("/email", methods=["GET"])
def get_user_email():
    """
    Sends the User Email back to the app given user_id
    
    Returns:
        A python dictionary containing status & a message key-value pair on a successful response
    """
    try:
        data = request.get_json()
        user_id = data["user_id"]
        user = User.objects(user_id=user_id)

        return jsonify({"status": True, "message": user.email}), 200
    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500

@profile.route("/other_user_details", methods=["POST"])
def get_other_user_details():
    """
    Sends the details of all users whose ids are mentioned in the user_id (key) of type list in the request body
    
    Returns:
        A python dictionary containing status & a response key-value pair on a successful response
    """
    result = {"status":False}
    content_type = request.headers.get('Content-Type')
    if content_type == current_app.config["JSON-CONTENT-TYPE"]:
        json_body = request.json
        user_ids = json_body.get('user_id',None)
    if user_ids is not None:
        try:
            users = User.objects.filter(user_id__in=user_ids)

            result["status"] = True
            result["response"] = users
        except Exception as e:
            traceback_message = traceback.format_exc()
            print(traceback_message)
            result['error'] = f"{e.__class__.__name__} occured"
            result['traceback'] = traceback_message
    
    else:
        result["response"] = "Missing Request Body key: 'user_id' should be a non-empty array"
    
    return result
