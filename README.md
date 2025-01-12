In this exercise, you will develop the backend for a web application for an accounting system and warehouse management. You will handle routes, form submissions, and data management.

1. Implement the backend functionality of the main page which displays the current stock level and account balance.

2. Handle form submissions for the purchase form, sale form, and balance change form. After the user submits data from these forms, refresh the page or print an error message if the data was not correct.

3. Implement the backend functionality for the "History" subpage. This page will retrieve two optional parameters (from, to):
   - /history/
   - /history/<line_from>/<line_to>/
   - If no parameters were given, display all history. If parameters were given, display only the history within the provided range.

4. Implement the functionality for reading and writing to a file for the history data.

Hints:

- Make sure to validate all data received from the user and think of errors that might occur during form submission.
- Remember to properly handle any errors that may occur during the file reading/writing process.
