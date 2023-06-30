 <h1 align=center><img src="static/images/logo.png" alt="Image Description" width="100" height="50">TRMMR </h1>

## Introduction
TRMMR is a web-based tool that allows users to shorten long URLs into shorter and more manageable links. It provides a simple, user-friendly interface to generate short URLs, track clicks, and manage the URLs and also user data.

The application is built using the Flask framework, a lightweight and extensible web framework for Python. It utilizes a SQLite database for storing URL mappings and tracking url clicks. The frontend is designed using HTML, CSS, and JavaScript, with support for generating QR codes for shortened URLs.
And also other necessary libraries like matplotlib for generating charts for analytics, flask-cache for caching and also flask-limiter for rate limiting etc. 

## Architecture
The application follows a client-server architecture. The server is built using Flask, which handles the requests 
and provides responses. The server interacts with a database to store the shortened URLs and their 
corresponding 
original URLs and also user data.

## Extensions Used
The application utilizes these major extensions to enhance its functionality:

1. **Matplotlib**: is a popular data visualization library used for creating various types of charts and plots. In the 
   TRMMR application, Matplotlib is used to generate bar and pie charts to visualize analytics data, such as the 
   number of 
   clicks on each shortened URL per day and also the platforms (OS) from which those clicks were made. This provides 
   users 
   with a graphical 
   representation of the 
   URL usage and engagement.

2. **Flask-Cache**: is a Flask extension that provides caching support for improving the performance of web applications.
   In the Flask URL shortener application, Flask-Cache is used to cache views and store temporary data, such as the 
   shortened URLs for users. Caching helps reduce the need for expensive computations or database queries, 
   improving the response time and overall application performance.

3. **Flask-Limiter:** is another Flask extension used for rate limiting requests to protect the 
   application 
   from excessive traffic. In this application, Flask-Limiter is used to enforce rate limits on certain endpoints, 
   such as the URL shortening endpoint. Rate limiting ensures that the application remains available and responsive by limiting the number of requests that can be made within a specified time frame.
4. **Flask-SQLAlchemy**: a Flask extension that simplifies database integration and provides an ORM layer for 
   interacting with databases. In the URL Shortener application, Flask-SQLAlchemy is used for defining database models, such as the ShortenedURL and User models. It provides an intuitive and Pythonic interface for querying and manipulating database records, making it easier to work with the database in a Flask application.

Other extensions used are Flask-Login,Flask-WTforms, Flask-Mail etc.
## Features
TRMMR offers the following features:

1. **Shorten long URLs:** Users can input a long URL and generate a shorter, more compact and unique version. The application generates a unique shortcode for each URL, which is used to access the original URL when the shortened link is visited.
2. **Customizable URLs:** Users have the option to customize the shortcode of their shortened URL by providing a custom alias.
3. **Click Tracking and Analytics:** The application tracks the number of clicks received for each shortened URL. Users can view analytics data such as total clicks, clicks per day, and the most clicked day for each shortened URL with graphical representation.
4. **QR Code Generation:** The application generates QR codes for each shortened URL, making it convenient for users to download and share URLs across devices.
5. **History:** For users who would like to browse through URLs they previously shortened, the application also includes a history feature. URLs that were shortened by a user are stored and made accessible to users any time.  
6. **Password-Protected URLs:** One unique feature about this application is the option to secure shortened URLs 
   with passwords. For users that want to shorten and secure URLs contain sensitive data, you can choose to protect 
   your shortened URLs with a password 
   for added security. 

## Installation
To set up the URL Shortener application, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/klvxn/trmmr
   ```
2. Change into the project directory:
   ```
   cd trmmr
   ```
3. Create a virtual environment:
   ```
   python3 -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
5. Update the package installer and install the required dependencies:
   ```
   pip install --upgrade pip && pip install -r requirements.txt
   ```

6. To run and use the application locally, follow the steps above and execute this command:

```
flask --app app run
```

By default, the application will be accessible at `http://localhost:5000`. You can change the host and port by specifying the `--host` and `--port` options with the `flask run` command.


## Usage and How-tos.


With the application now running, you can test out all the functionalities of the application. 
From the home page, click the _SIGN UP_ button to create a new account. This would give you access to all the 
features of the application as unauthenticated users are restricted to shortening URLs only. 
***
![Screenshot (279)](https://github.com/Klvxn/TRMMR/assets/64833055/962b569d-fbdb-404f-81da-bf87ae1336f0)

***
1. Generating short URLs: Go to the home page and on the input form, paste in a long URL you'd like to trim and 
   click the _TRM_ button. A new clean and short URL would be generated for you.
2. Customizing shortened URLs: To customize the short URL to your taste, there's a second input form that allows to 
   the second half of the generated URL. Enter what you prefer and just like before, click the _TRM_ button
   <br> All blank spaces will be converted to hyphens.
3. Generating QR Codes: With the short URL generated for you, you have an option to generate a QR code for the URL 
   immediately. To do this, just below the newly created URL, click the Generate QR code button and a box-sized QR 
   code image will be generated for you. You can also download this image to your device and share it. <br>
Another way to generate a QR code is to click on _QR CODES_ in the side navigation bar. In this page, you can just 
   paste in a short or long URLs and generate the QR code image and also download it to your device. 
4. Securing shorten URLs with password:  For users that would want to shorten URLs that contain sensitive information 
   or data that 
   you'd want to keep from everyone else except yourself, you can shorten a URL and secure it with a password. Any 
   user that clicks on the shorten URL will be redirected to a page to input the password to the URL before they are 
   redirected to the main URL. <br>
    To use this feature, after generating a new short URL, click the _SECURE URL_ button. This button would create a 
   password input form for you to secure your URL. Enter the URL and submit. <br>
    NOTE: You won't be able to recover your URL if you lost the password.
5. Viewing and clearing your TRMMR history: To see a history of URLs you've previously shortened, click
   _HISTORY_ on 
   the side navigation tab. This would take show you a list of all your URLs, with their respective creation dates. 
   Below the list, you have the CLEAR HISTORY button that will wipe all your generated URLs from the database, and 
   give you the chance to start fresh.
6. Viewing analytics: For each URL in your TRMMR history, you can view analytics and monitor how your shortened 
   URL has been performing. On the history page, click on the VIEW ANALYTICS link. In this page, you can view the 
   number of clicks on your shortened URL,
   day it was last visited, day with the most clicks, 
   etc. with graphical representation to show you this data. 
7. Othes: On the sidebar, you can also update your information including email, first and last names and even have 
   the option to deleter your account. 

## Acknowledgements
TRMMR is built on top of the Flask micro web framework and utilizes various open-source libraries and 
extensions. The development of this application was inspired by the need for a simple and efficient URL shortening 
solution. I would like to thank the Flask community, the contributors of the used extensions, and all the developers 
involved in creating the underlying technologies. And also the tutors and everyone at [Altschool Africa](https://altschoolafrica.com) for the oppoturnity to be 
build this application as the capstone project.

## License
The TRMMR application is open source and released under the [MIT License](LICENSE). You are free to use, modify, and distribute the application according to the terms of the license.

## Contributing
Contributions to TRMMR are welcome! If you find any issues or have suggestions for improvements, please feel free to submit a pull request or open an issue on the project's GitHub repository.