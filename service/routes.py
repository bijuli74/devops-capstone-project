"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for   # noqa; F401
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    location_url = url_for("get_accounts", account_id=account.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# LIST ALL ACCOUNTS
######################################################################

@app.route("/accounts", methods=["GET"])
def get_accounts():
    """ Fetches all the Accounts """
    app.logger.info("Request to list Accounts")
    accounts = list(Account.all())
    serialized_accounts = [account.serialize() for account in accounts]
    return make_response(jsonify(serialized_accounts), status.HTTP_200_OK)

######################################################################
# READ AN ACCOUNT
######################################################################

@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    """ Read details of an Account with account id """ 
    app.logger.info("Request to read an Account with id: %s", account_id)

    account = Account.find(account_id)
    if account is None:
        abort(status.HTTP_404_NOT_FOUND, "Account not found")
    
    return make_response(jsonify(account.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################

@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    """ Update an account using account id """

    app.logger.info("Request to update an Account with id: %s", account_id)
    account = Account.find(account_id)
    if account is None:
        abort(status.HTTP_404_NOT_FOUND, "Account not found")
    
    check_content_type("application/json")
    account.deserialize(request.get_json())
    account.update()

    return make_response(jsonify(account.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE AN ACCOUNT
######################################################################

@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_an_account(account_id):
    """ Delete an account based an account id """

    app.logger.info("Request to delete an Account with id: %s", account_id)
    account = Account.find(account_id)
    if account is None:
        return make_response("", status.HTTP_204_NO_CONTENT)
    
    account.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)
    
######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )

