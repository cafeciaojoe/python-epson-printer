import subprocess

while True:
    try:
        # Run the email-checking script
        subprocess.run(["python", "email_check_thermal_print.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running email_check_print.py: {e}")