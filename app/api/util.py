def reset_api():
    return {
        "code": 200,
        "message": "Successful to reset"
    }


def config_api_success():
    return {
        "code": 200,
        "message": "Successful to config"
    }


def seats_error():
    return {
        "code": 400,
        "message": "number of seats is invalid"
    }


def seats_success(seats):
    return {
        "message": "Success",
        "numbers": len(seats),
        "seats": seats,
    }


def reserve_error_location():
    return {
        "code": 400,
        "message": "Cannot reserve because you dont have choice location"
    }


def reserve_error_rules():
    return {
        "code": 400,
        "message": "violation rules"
    }


def reserve_success():
    return {
        "code": 200,
        "message": "Success reserve"
    }
