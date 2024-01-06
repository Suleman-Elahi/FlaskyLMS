# FlaskyLMS

Streamline your leave management process with ease.

FlaskyLMS is a self-hosted Flask application that empowers employees to request leaves seamlessly and admins to manage those requests efficiently. It integrates seamlessly with email notifications and Google Calendar to keep everyone in the loop and organized.

## Key Features:

* **User-friendly leave request process**: Employees can easily submit leave requests through a simple and intuitive interface.

* **Admin approval and rejection**: Admins can review leave requests, approve or reject them, and provide feedback if needed.

* **Email notifications**: Both employees and admins receive timely email notifications for new requests, approvals, and rejections.

* **Google Calendar integration**: Approved leaves are automatically added as events to the admin's Google Calendar, ensuring visibility and avoiding scheduling conflicts.

* **Self-hosted**: Host the application on your own server for complete control and data privacy.

## Installation:

### Clone the repository:

`git clone https://github.com/your-username/FlaskyLMS.git`

### Install dependencies:

`cd FlaskyLMS`

`pip install -r requirements.txt`

### Fill the proper details in the `.env` file:

* Add the SMTP Details
* Add Google Cloud Service Account File path (service.json), [See this](https://medium.com/iceapple-tech-talks/integration-with-google-calendar-api-using-service-account-1471e6e102c8#:~:text=Navigate%20to%20https%3A%2F%2Fadmin,and%20login%20with%20admin%20credentials.&text=Add%20a%20new%20Client.&text=It%20will%20download%20the%20JSON,Private%20Key%20and%20other%20details.)
* Add default user and password.
* Add Gmail address.
* Add Admin email to receive leave requests.

### Run the application:

`python index.py`

## Screenshots:
![enter image description here](https://res.cloudinary.com/suleman/image/upload/v1704538611/FlaskyLMS.png)
## Contribute:

I welcome contributions to FlaskyLMS! Feel free to submit pull requests or open issues for any enhancements or bug fixes.

## License:

FlaskyLMS is licensed under the MIT License.
