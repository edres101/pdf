
import os
import re
import time
import shutil
import pdfplumber
import pytesseract
from tqdm import tqdm
from getpass import getpass
from pytesseract import image_to_string
from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter, PdfMerger


# Path to the Tesseract executable (change this according to your installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# pytesseract.pytesseract.tesseract_cmd = r'tesseract.exe'

# To Convert python file to .exe:
#pyinstaller --clean --onefile --icon=brain.ico --paths 'C:\Users\user\Desktop\my-projects\pdf\env\Lib\site-packages' --add-data 'C:\Program Files\Tesseract-OCR;.' main.py


# Global Variables
files_name_for_extraction = []
files_path_for_extraction = []

numbers = []
b_numbers = []

files_name_for_separation = []
files_path_for_separation = []

output_files_path = []

files_number_and_bnumber = {}

bawa_numbers = {}
all_texts = []  
bawa_output_files_path = []



def login():
    # Define the correct password
    correct_password = "0000"
    
    # Repeat until the correct password is entered or the user quits
    while True:
        # Ask the user to enter the password
        entered_password = getpass("Enter the password (or 'Q' to quit): ")
        
        # Check if the user wants to quit
        if entered_password.upper() == 'Q':
            print("\nExit...")
            return False
        
        # Check if the entered password matches the correct password
        if entered_password == correct_password:
            print("\nLogin successful!")
            return True
        else:
            print("\nIncorrect password. Please try again.")





def extract_pdf_numbers_data(input_folder_data):
    # Iterate over each file in the folder
    for file_name in tqdm(os.listdir(input_folder_data), desc='Extracting Data from pdf files'):
        if file_name.endswith(".pdf"):
            # Construct the full file path
            files_name_for_extraction.append(file_name)
            file_path = os.path.join(input_folder_data, file_name)
            files_path_for_extraction.append(file_path)
            
            # Open the PDF file using pdfplumber
            with pdfplumber.open(file_path) as pdf:
                # Extract text from each page
                for i, page_num in enumerate(range(len(pdf.pages))):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    
                    if matches := re.search(r'\d+\s+\b(\d{8})\b\s+\d+', text):
                        b_numbers.append(matches.group(1))
                    else:
                        b_numbers.append('None')
                        
                    if number := re.search(r':+\s*(\d+)', text[:200]):
                        number = number.group(1)
                        
                        
                        if number in numbers:
                            numbers.append(f'{number}_{i}_duplicated')
                        else:
                            numbers.append(number)
                        
                    
                    # Process extracted text as needed
                    # print(f"Text from {file_name}, Page {page_num + 1}:")
                    # print(text[:700])
                    # print(numbers)
                    # print(b_numbers)
                    # print("---------------------------------------------")
                    
                    
                    
    # Create a new dictionary and filter items to remove the duplicated one.
    my_dict = {k: v for k, v in zip(numbers, b_numbers)}
    my_dict = {key: value for key, value in my_dict.items() if not key.endswith('_duplicated')}
    files_number_and_bnumber.update(my_dict)




    
def separate_pdf_pages_data(input_folder_data, output_folder_data):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder_data):
        os.makedirs(output_folder_data)
        
            # Iterate over each file in the folder
    for file_name in tqdm(os.listdir(input_folder_data), desc='Separating Pdf files Data'):
        if file_name.endswith(".pdf"):
            # Construct the full file path
            files_name_for_separation.append(file_name)
            file_path = os.path.join(input_folder_data, file_name)
            files_path_for_separation.append(file_path)
            
            for file in files_path_for_separation:

                # Open the input PDF file
                with open(file, 'rb') as f:
                    pdf_reader = PdfReader(f)

                    # Iterate through each page
                    for page_num in range(len(pdf_reader.pages)):
                        
                        # Create a new PdfWriter object for each page
                        pdf_writer = PdfWriter()
                        pdf_writer.add_page(pdf_reader.pages[page_num])
                        
                        if len(numbers) < 1:
                            
                            # Construct the output file path
                            output_file = os.path.join(output_folder_data, f"Page_{page_num+1}.pdf")
                            output_files_path.append(output_file)
                        
                        else:
                            # Construct the output file path
                            output_file = os.path.join(output_folder_data, f"Y_{numbers[page_num]}.pdf")
                            output_files_path.append(output_file)
                        
                        

                        # Write the page to the output file
                        with open(output_file, 'wb') as output:
                            pdf_writer.write(output)
            
            
                
      
                
def remove_files_in_directory_data(directory):
    # Iterate over each file in the directory
    for filename in tqdm(os.listdir(directory), desc='Removing duplicated pdf files Data'):
        # Construct the full file path
        file_path = os.path.join(directory, filename)
        # Check if the path is a file
        if os.path.isfile(file_path):
            # Check if the filename ends with 'duplicate' and has .pdf extension
            if filename.endswith('duplicated.pdf'):
                # Remove the file
                os.remove(file_path)
                
                
      
      
            
def rename_files_data(directory):           
    # Iterate over each file in the directory
    for file_name, new_name in tqdm(files_number_and_bnumber.items(), desc='Renaming pdf files Data'):
        # Construct the old and new file paths
        file_name= f'Y_{file_name}.pdf'
        old_file_path = os.path.join(directory, file_name)
        new_filename = f"Y_{new_name}.pdf"  # Rename according to your requirement
        new_file_path = os.path.join(directory, new_filename)
        
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
            os.rename(old_file_path, new_file_path)
            
        else:
            # Rename the file
            os.rename(old_file_path, new_file_path)

                


                        
def extract_text_from_scanned_pdfs_bawa(directory):
    
        
    # Iterate over each file in the folder.
    for file_name in tqdm(os.listdir(directory), desc='Extracting Text from PDF files'):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(directory, file_name)
    
            # Convert PDF to images.
            images = convert_from_path(file_path)

            # Extract the first page text.
            first_page_text = image_to_string(images[0])
            
            # Extract the bawa number and attached it to dict as a value for each pdf file.
            if matches := re.search(r'\b(\d{4}\s?\d{4})\b', first_page_text):
                    bawa_numbers[f'{file_name}'] = matches.group(1).replace(" ", "")
                    
            else:
                bawa_numbers[f'{file_name}'] = 'None'

            # Append text from current PDF to list
            all_texts.append(first_page_text)





def separate_pdf_pages_bawa(input_folder_data, output_folder_data):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder_data):
        os.makedirs(output_folder_data)
    
    # Iterate over each file in the folder
    for i, file_name in tqdm (enumerate(os.listdir(input_folder_data)), desc='Separating PDF pages'):
        file_path = os.path.join(input_folder_data, file_name)

        # Open the input PDF file
        with open(file_path, 'rb') as f:
            pdf_reader = PdfReader(f)

            # Check if the PDF has any pages
            if len(pdf_reader.pages) > 0:
                # Create a new PdfWriter object for the first page
                pdf_writer = PdfWriter()
                pdf_writer.add_page(pdf_reader.pages[0])  # Add the first page only
                
                if bawa_numbers[file_name] == 'None':
                    
                    # Construct the output file path
                    output_file = os.path.join(output_folder_data, f"B_None_{i}.pdf")
                
                else:
                    # Construct the output file path
                    output_file = os.path.join(output_folder_data, f"B_{bawa_numbers[file_name]}.pdf")

                # Write the first page to the output file
                with open(output_file, 'wb') as output:
                    pdf_writer.write(output)





def merge_pdfs(bawa_folder, data_foler, merged_folder):
    
    # Create the merged folder if it doesn't exist
    if not os.path.exists(merged_folder):
        os.makedirs(merged_folder)
        
    # Iterate over files in folder A
    for file_A in tqdm(os.listdir(bawa_folder), desc='Merging Pdf files'):
        if file_A.endswith('.pdf'):
            # Extract the number from the file name
            number_A = os.path.splitext(file_A)[0][2:]

            # Iterate over files in folder B
            for file_B in os.listdir(data_foler):
                if file_B.endswith('.pdf') and file_B.endswith(number_A + '.pdf'):
                    # Merge the PDFs
                    merger = PdfMerger()
                    merger.append(os.path.join(bawa_folder, file_A))
                    merger.append(os.path.join(data_foler, file_B))

                    # Save the merged PDF to folder C
                    output_file = os.path.join(merged_folder, f'M_{number_A}.pdf')
                    with open(output_file, 'wb') as output:
                        merger.write(output)
                        
                        
    
    
                        
def final_merge_pdfs(output_folder_merged, output_folder_final):
    
    # Initialize PDF merger
    merger = PdfMerger()

    # Iterate over files in folder A
    for filename in tqdm(os.listdir(output_folder_merged), desc='Final Merge for Pdfs'):
        if filename.endswith('.pdf'):
            # Get the full path of the PDF file
            file_path = os.path.join(output_folder_merged, filename)

            # Append the PDF to the merger
            merger.append(file_path)

    # Create the output directory if it doesn't exist
    os.makedirs(output_folder_final, exist_ok=True)

    # Write the merged PDF to folder B
    output_path = os.path.join(output_folder_final, 'Final_Result.pdf')
    with open(output_path, 'wb') as output_file:
        merger.write(output_file)





def get_file_numbers(folder):
    numbers = set()
    for filename in os.listdir(folder):
        if filename.endswith('.pdf'):
            # Extract the number from the filename
            number = filename.split('_')[-1].split('.')[0]
            numbers.add(number)
    return numbers





def copy_files_with_different_numbers(bawa_folder, data_folder, different_folder):
    numbers_A = get_file_numbers(bawa_folder)
    numbers_B = get_file_numbers(data_folder)
    
    # Create different_folder if it doesn't exist that will contain all different pdf files name form both folder.
    os.makedirs(different_folder, exist_ok=True)

    # Copy files from folder (Bawa) to folder (Different) if their numbers don't exist in folder (Data)
    for filename in tqdm(os.listdir(bawa_folder), desc='Moving different Bawa'):
        if filename.endswith('.pdf'):
            number = filename.split('_')[-1].split('.')[0]
            if number not in numbers_B:
                src = os.path.join(bawa_folder, filename)
                dst = os.path.join(different_folder, filename)
                shutil.copyfile(src, dst)
                
    print('\n')

    # Copy files from folder B to folder C if their numbers don't exist in folder A
    for filename in tqdm(os.listdir(data_folder), desc='Moving different Data'):
        if filename.endswith('.pdf'):
            number = filename.split('_')[-1].split('.')[0]
            if number not in numbers_A:
                src = os.path.join(data_folder, filename)
                dst = os.path.join(different_folder, filename)
                shutil.copyfile(src, dst)





def main():
    
    if login():
        
        while True:
            
            
            print('''
                Choose a Number:
                1. Whole Process
                2. Merging pdf files
                3. Separating pdf files 
                ''')
            
            number = str(input('Enter a number (1, 2, or 3) or (Q) to Exit: '))
            
            while number not in ['1', '2', '3', 'q', 'Q']:
                number = str(input('Please Enter a valid number or (Q) to Exit: '))
                
            if number == 'q' or number == 'Q':
                return print('Exit...')
            
            else:
                
                
                    
                match number:
                    case "1":
                    
                        # Input Folders
                        input_folder_bawa = input('\nEnter AWB Folder Directory: ').replace('\\','/').replace('"', '')
                        
                        while '/' not in input_folder_bawa:
                            input_folder_bawa = input('\nPlease Enter a valid AWB Folder Directory: ').replace('\\','/').replace('"', '')
                            
                        input_folder_data = input('\nEnter BAYAN Folder Directory: ').replace('\\','/').replace('"', '')
                        
                        while '/' not in input_folder_data:
                            input_folder_data = input('\nPlease Enter a valid BAYAN Folder Directory: ').replace('\\','/').replace('"', '')
                        print('\n')
                        
                        
                        
                        # Output Folders
                        output_folder_bawa = os.getcwd() + r'\awb'
                        output_folder_data = os.getcwd() + r'\bayan'
                        output_folder_merged = os.getcwd() + r'\merged'
                        output_folder_final = os.getcwd() + r'\final-result'
                        output_folder_different = os.getcwd() + r'\different'
                        
                        
                        # Measure execution time
                        start_time = time.time()
                        
                        # Data Functions
                        extract_pdf_numbers_data(input_folder_data) 
                        print('\n')
                        separate_pdf_pages_data(input_folder_data, output_folder_data)
                        print('\n')
                        remove_files_in_directory_data(output_folder_data)
                        print('\n')
                        rename_files_data(output_folder_data)
                        print('\n')
                        
                        
                        # Bawa Functions
                        extract_text_from_scanned_pdfs_bawa(input_folder_bawa)
                        print('\n')
                        separate_pdf_pages_bawa(input_folder_bawa, output_folder_bawa)
                        print('\n')
                        
                        # Both Functions
                        merge_pdfs(output_folder_bawa, output_folder_data, output_folder_merged)
                        print('\n')
                        final_merge_pdfs(output_folder_merged, output_folder_final)
                        print('\n')
                        copy_files_with_different_numbers(output_folder_bawa, output_folder_data, output_folder_different)
                        print('\n')

                        end_time = time.time()
                        
                        
                        elapsed_time = end_time - start_time
                        print(f"\nProcesses Successfully Done During: {elapsed_time / 60} minutes")
                        
                        
                    case "2":
                        
                        # Input Folders
                        input_folder = input('\nEnter Folder Directory to merge files: ').replace('\\','/').replace('"', '')
                        output_folder_merged = os.getcwd() + r'\merged0'
                        print('\n')
                        
                        # Measure execution time
                        start_time = time.time()
                        
                        final_merge_pdfs(input_folder, output_folder_merged)
                        
                        end_time = time.time()
                        
                        elapsed_time = end_time - start_time
                        print(f"\nProcesses Successfully Done During: {elapsed_time / 60} minutes")
                        
            
                    case "3":
                        
                        # Input Folders
                        input_folder = input('\nEnter Folder Directory to separate files: ').replace('\\','/').replace('"', '')
                        output_folder_separated = os.getcwd() + r'\separated0'
                        print('\n')
                        
                        # Measure execution time
                        start_time = time.time()
                        
                        separate_pdf_pages_data(input_folder, output_folder_separated)
                        
                        end_time = time.time()
                        
                        elapsed_time = end_time - start_time
                        print(f"\nProcesses Successfully Done During: {elapsed_time / 60} minutes")
            
            
            key = str(input('\nEnter (Q) to Exit or press any key to continue: '))
            
            if key.upper() == 'Q':
                print('\nExit...')
                break
                    
    else:
        return


if __name__ == '__main__':
    main()


            
