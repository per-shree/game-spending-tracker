# Game Spending Tracker

A web application to help parents and gamers track, manage, and control gaming expenses.

## Features

- **Track Game Purchases**: Record and categorize all your gaming expenses
- **Spending Limits**: Set monthly budgets for game-related purchases
- **Parental Controls**: Parents can approve or deny children's game purchase requests
- **Dashboard**: View spending statistics and transaction history
- **Multi-platform Support**: Track spending across different gaming platforms

## Screenshots

*Coming soon*

## Tech Stack

- **Backend**: Python with Flask framework
- **Frontend**: HTML, CSS, Bootstrap 5
- **Database**: File-based JSON storage
- **Icons**: Font Awesome 5

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/game-spending-tracker.git
   cd game-spending-tracker
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install flask
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage

1. Register a new account
2. Log in with your credentials
3. Add game purchases through the "Record Spending" page
4. Review and approve/deny pending transactions
5. View statistics and transaction history on your dashboard

## Demo Account

You can use the "Add Sample Data" button on the dashboard to populate your account with sample transactions.

## Project Structure

- `app.py`: Main application file with Flask routes and logic
- `data/`: Directory for user data storage
- Templates are embedded in the application for simplicity

## Future Enhancements

- User profiles with avatars
- Graphs and charts for spending analysis
- Multiple family member accounts
- Receipt image upload
- Export data functionality
- Mobile app version

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

- Shree Ugale - Initial work

## Acknowledgments

- Bootstrap for the responsive design framework
- Font Awesome for the icons
