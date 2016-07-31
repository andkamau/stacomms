# Virtual Communications Slip

Enables users to:
* Raise issues (via Google Form)
* Responses are provided on the Google Sheet generated by the form.
* Email and SMS notifications are sent to those who raised the issue (once there is a response)

Deployment
* App backend is running on Amazon EC2
* Website hosted on Amazon S3
* Static data stored in MySQL
* Dynamic data stored in Redis
* Issues are raised / submitted on an embedded Google Form
* Raised issues are stored on Google Sheets
* Services
  - Consumer ONE
  - Consumer TWO
  - Web service (Twisted)
  - Responses server (Twisted)
  - Website (S3 and Jekyll)

External dependencies:
* Google Sheets API (via https://github.com/andkamau/gspread)
* Pythias push messaging (https://bitbucket.org/pythias_io/push_messaging/)
* Jekyll (jekyllrb.com)
* Mysql
* Redis
