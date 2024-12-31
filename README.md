**Nigerian National Identification Number (NIN) Validation API**
===========================================================

**Overview**
------------

This API provides a simple and efficient way to validate Nigerian National Identification Numbers (NIN). The NIN is a unique 11-digit number assigned to every Nigerian citizen, and this API helps to verify its authenticity.

**Endpoints**
------------

### Validate NIN

* **URL:** `/get_validation/`
* **Method:** `POST`
* **Request Body:**
	+ `nin`: The 11-digit NIN to be validated
    + `day`: Day of birth
    + `month`: Month of birth, example: `Jan`, `Feb`, `Mar`, `Apr`, ... `Sep`, `Oct`, `Nov`, `Dec`
    + `year`: Year of birth 
* **Response:**
	+ `message`: A payload providing additional information about the validation result

**Example Request**
```json
{
  "nin": "12345678901",
  "day": "06",
  "month": "Oct",
  "year": "2015"
}
```

**Example Response**
```json
{
    "First Name": "JOHN",
    "Middle Name": "SINCLAIR",
    "Last Name": "DOE",
    "Date of Birth": "06-10-2015",
    "Gender": "MALE",
    "Marital Status": "SINGLE",
    "Place of Birth": "Akure Ondo",
    "Maiden Name": ""
}
```

**Validation Rules**
------------------

The API uses the following rules to validate the NIN:

* The NIN must be an 11-digit number
* The NIN must not contain any non-numeric characters
* Month must be in the format `Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`...


**API Documentation**
--------------------

This API is built using FastAPI Framework and follows standard API documentation guidelines.

**Contributing**
---------------

Contributions are welcome! Please submit a pull request with your changes, and ensure that you follow the standard coding guidelines.

**Contact**
----------

For any questions or concerns, please contact Saleem Adebayo at bayoleeems@gmail.com