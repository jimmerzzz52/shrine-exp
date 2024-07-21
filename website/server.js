const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const nodemailer = require('nodemailer');
const dotenv = require('dotenv');
const fs = require('fs');

dotenv.config();

const app = express();

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json()); // Add this line to parse JSON bodies

// Serve static files from the root directory
app.use(express.static(__dirname));

app.post('/submit', (req, res) => {
    const { name, phone, email, message } = req.body;
    console.log(`Received form data: Name: ${name}, Phone: ${phone}, Email: ${email}, Message: ${message}`);
    
    // Email sending logic
    const transporter = nodemailer.createTransport({
        host: process.env.SMTP_HOST,
        port: process.env.SMTP_PORT,
        secure: process.env.SMTP_SECURE === 'true',
        auth: {
            user: process.env.SMTP_USER,
            pass: process.env.SMTP_PASS
        }
    });

    const mailOptions = {
        from: process.env.SMTP_USER,
        to: process.env.RECIPIENT_EMAIL,
        subject: 'New Contact Form Submission',
        text: `Name: ${name}\nPhone: ${phone}\nEmail: ${email}\nMessage: ${message}`
    };

    transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
            console.error('Error sending email:', error);
            // Log error to a file
            fs.appendFile('error.log', `${new Date().toISOString()} - Error: ${error.message}\n`, (err) => {
                if (err) console.error('Failed to write to error log:', err);
            });
            res.status(500).send('An error occurred while sending the email. Please try again later.');
        } else {
            console.log('Email sent:', info.response);
            res.send('Thanks for contacting us, we will get back to you as soon as possible.');
        }
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
