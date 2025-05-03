# IGNOU Grade Card Details Convert into MySql Table


## Requirements

To run this program, you will need:

* **Python 3.6 or higher:** Ensure you have a compatible version of Python installed.
* **MySQL Server:** You need to have a MySQL server installed and running on your local machine. The program will connect to this instance.
* **Required Python Libraries:** The following libraries are necessary and will be installed using pip.

## Installation

* **Install Required Python Libraries:**

   Navigate to the program's directory in your terminal and install the necessary libraries using pip:

   ```bash
   cd program_directory
   pip install -r requirements.txt

## Usage

* **Change Variables in Source Code Before Run:**
    
    #### In grade_card.py
    ```code
    enrolment_number = Your Enrolment Number
    programme_code = "Your Programme Code"
    ```
    * For mysql configuration:
    ```code
    rootuser = mysql.connector.connect(
        host="Your hostname",
        user="Your Username",
        password="Your Password",
        port="Your port "
    )
    ```
    * After this change navigate to the program's directory in your terminal and run program like this:
    ```bash
    cd program_directory
    python grade_card.py
    ```
    If succesfully run program without an error than your details available in mysql database.

## Output

* **To see your details:**

    In the mysql CLI:
    ```bash
    mysql> use grade_cards;
    mysql> show tables;
    ```
    Hence you can see all details.
