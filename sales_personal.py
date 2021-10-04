from selenium.common.exceptions import ElementNotInteractableException, ElementNotVisibleException, NoSuchElementException, TimeoutException
import helpers
import user
from helpers import datetime,csv
from csv import reader


# Classes
class Sales():
    def __init__(self):
        pass

    def make_sale(self):
         #set data frame and make column list
        df = helpers.pd.read_csv(r'C:\Users\rford\Desktop\items.csv')
        #stops pandas from reading csv as floats
        data = df.fillna(0)
        item_ids = data['Item Numbers'].astype(int).tolist()
        #get saleManager.php
        helpers.driver.get("#")
        select = helpers.Select(helpers.driver.find_element_by_xpath('//*[@id="saleTypeId"]'))
        #prompt for sale type
        prompt = "Choose Sale Type:\n\t1: Email Special\n\t2: Catalog Sale\n"
        helpers.WebDriverWait(helpers.driver, 10)
        #1 for Email Sale #2 for Catalog Sale
        while True:
            try:
                sale_type = int(input(prompt))
                if sale_type < 1 or sale_type > 2:
                    raise ValueError
                break
            except ValueError:
                prompt = "Please enter 1 or 2:\n> "
        if sale_type == 1:
            select.select_by_value('1')
        else:
            select.select_by_value('2')
        #check 'Either' radio button on Currently Active
        helpers.driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/form[1]/div/ul/li[2]/input[3]').click()
        #check 'Either' radio button on Sold Online
        helpers.driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/form[1]/div/ul/li[1]/input[3]').click()
        #check 'Either' radio button on Sold to Customers
        helpers.driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/form[1]/div/ul/li[3]/input[3]').click()
        #check 'Either' radio button on Sales Taxable
        helpers.driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/form[1]/div/ul/li[4]/input[3]').click()
        #wait
        helpers.WebDriverWait(helpers.driver, 1)
        #Select Edit Item Form
        helpers.driver.find_element_by_xpath('//*[@id="choosSaleTypeForm"]/div/ul/li[2]/input').click()
        #wait
        helpers.WebDriverWait(helpers.driver, 3)
        #prompt for sale name
        sale_name = input("Enter Sale Name: ")
        helpers.WebDriverWait(helpers.driver, 10)
        helpers.driver.find_element_by_xpath('//*[@id="subject"]').send_keys(sale_name)
        #prompt for expiration and add to datepicker
        expiration_date = input("Enter Expiration Date in format YYYY-MM-DD HH:MM:SS:\n")
        print("Expiration Date Added")
        helpers.driver.find_element_by_xpath('//*[@id="expireDateTime"]').clear()
        helpers.driver.find_element_by_xpath('//*[@id="expireDateTime"]').send_keys(expiration_date)
        #Set save sale variable
        save_sale = helpers.driver.find_element_by_xpath('//*[@id="editSaleForm"]/div/p/input')
        save_sale.click()
        #delete items showing from previous sale
        helpers.driver.find_element_by_xpath('//*[@id="regsearch"]/form[2]/div/ul/li[4]/input').click()
        #save
        save_sale.click()
        #choose from available inventory
        inv_avail = input('Inventory Available? Y/N  ')
        if inv_avail == 'Y':
            helpers.driver.find_element_by_xpath('//*[@name="isInStock"]').click()
            print('Selecting From Available Inventory...')
        else:
            pass
        #wait
        helpers.WebDriverWait(helpers.driver, 10)
        # for each item number in list add to sale
        for item_number in item_ids:
            helpers.driver.find_element_by_xpath('//*[@id="name"]').clear()
            helpers.WebDriverWait(helpers.driver, 10)
            helpers.driver.find_element_by_xpath('//*[@id="name"]').send_keys(item_number)
            helpers.WebDriverWait(helpers.driver, 10)
            helpers.driver.find_element_by_xpath('//*[@id="searchinputs"]/div/div[2]/div[3]/input[3]').submit()
            helpers.WebDriverWait(helpers.driver, 10)
            add_to_list_id = 'addToList_{}'.format(item_number)
            ignored_exceptions=(helpers.NoSuchElementException, helpers.StaleElementReferenceException)
            add_to_list = helpers.WebDriverWait(helpers.driver, 10, ignored_exceptions=ignored_exceptions).until(helpers.expected_conditions.presence_of_element_located((helpers.By.ID, add_to_list_id)))
            add_to_list.click()
            helpers.WebDriverWait(helpers.driver, 5)
            print('Item {} has been added to Sale!'.format(item_number))
        print('Sale Creation Complete!')
        helpers.WebDriverWait(helpers.driver, 20)
        save_sale_id = 'saveItemList'
        save_sale_items = helpers.WebDriverWait(helpers.driver, 10, ignored_exceptions=ignored_exceptions).until(helpers.expected_conditions.presence_of_element_located((helpers.By.NAME, save_sale_id)))
        save_sale_items.click()
        helpers.WebDriverWait(helpers.driver, 20)

    def get_report_data(self):
        helpers.driver.get('#')
        current_date = helpers.currentDate
        helpers.WebDriverWait(helpers.driver, 10)
        #Create Dataframe
        df = helpers.pd.read_csv(r'C:\Users\rford\Desktop\sale_ids.csv')
        #Parse to Text
        data = df.fillna(0)
        #set ids from each column list
        everyone_ids = data['Everyone'].astype(int).tolist()
        dd_ids = data['Daily Deal'].astype(int).tolist()
        targeted_ids = data['Targeted'].astype(int).tolist()
        push_ids = data['Push Notification'].astype(int).tolist()
        acq_ids = data['Acquisition'].astype(int).tolist()
        #loop through each sale id by sale type
        for form_code, sales_type, idlist in (
        ( 1, "Everyone", everyone_ids ),
        ( 1, "Daily Deal", dd_ids ),
        ( 2, "Targeted", targeted_ids ),
        ( 2, "Push Notification", push_ids ),
        ( 2, "Acquisition", acq_ids ) ):
            results = []
            print('Gathering {} Sale Information'.format(sales_type))
            while any(idlist):
                sale_id = idlist.pop(0)
                #Grab sale option for each form id and sale id
                helpers.driver.find_element_by_xpath('/html/body/form[{}]/div/select/option[@value={}]'.format(form_code, sale_id)).click()
                helpers.WebDriverWait(helpers.driver, 20)
                #Parse date created from title
                date_created = helpers.driver.find_element_by_xpath('/html/body/form[{}]/div/select/option[@value={}]'.format(form_code, sale_id)).text[:10]
                #Parse expiration date created from title
                exp_date = helpers.driver.find_element_by_xpath('/html/body/form[{}]/div/select/option[@value={}]'.format(form_code, sale_id)).text[-19:-9]
                #Parse Sale Code from title
                sale_code = helpers.driver.find_element_by_xpath('/html/body/form[{}]/div/select/option[@value={}]'.format(form_code, sale_id)).text[11:17]
                #Submit form
                helpers.driver.find_element_by_xpath('/html/body/form[{}]/div/input[1]'.format(form_code)).submit()
                helpers.WebDriverWait(helpers.driver, 1)
                #Get Sale title from table
                title = helpers.driver.find_element_by_xpath('/html/body/h2[2]').text or "N/A"
                #Get total sold from table
                sold = helpers.driver.find_element_by_xpath('/html/body/table[1]/tbody/tr[last()]/td[4]').text or "0"
                # cost = helpers.driver.find_element_by_xpath('/html/body/table[1]/tbody/tr[last()]/td[6]').text[1:] or "0"
                # price = helpers.driver.find_element_by_xpath('/html/body/table[1]/tbody/tr[last()]/td[7]').text[1:] or "0"
                # profit = helpers.driver.find_element_by_xpath('/html/body/table[1]/tbody/tr[last()]/td[8]').text[1:] or "0"
                # addSales = helpers.driver.find_element_by_xpath('/html/body/table[1]/tbody/tr[last()]/td[9]').text[1:] or "0"
                # addProfit = helpers.driver.find_element_by_xpath('/html/body/table[1]/tbody/tr[last()]/td[10]').text[1:] or "0"

                #add results to list
                results.append([title, sold, sale_id, date_created, current_date, exp_date, sales_type, sale_code])
                print([title, sold, sale_id, date_created,current_date, exp_date, sales_type, sale_code])
            print("{} Data Gathered".format(sales_type))
            #write to CSV
            with open(r'C:\Users\rford\Desktop\Richard Ford\Results\{}_results.csv'.format(sales_type), 'w+', newline='', encoding='utf-8') as file:
                writer = helpers.csv.writer(file)
                writer.writerow((['Title', 'Sold', 'Sale ID', 'Created Date', 'Current Date', 'Expiration Date', 'Sale Type', 'Code']))
                writer.writerows(results)
                print('{} CSV Created\n'.format(sales_type))
                #Set Columns for CSV
                
    def coupon_results(self):
        print('Starting Promo Code Results....')
        results = []
        df = helpers.pd.read_csv(r'C:\Users\rford\Desktop\promo_codes.csv')
        data = df.fillna(0)
        code_names = data['Codes'].astype(str).tolist()
        helpers.WebDriverWait(helpers.driver, 10)
        helpers.driver.get('#')
        set_date = helpers.driver.find_element_by_xpath('//*[@id="daterange"]')
        helpers.driver.execute_script("arguments[0].click();", set_date )
        # date = helpers.driver.find_element_by_id('daterange')
        # date.clear()
        # date.send_keys(search)
        for code_name in code_names:
            select = helpers.driver.find_element_by_id('globalMenuInfo')
            for option in select.find_elements_by_tag_name('option'):
                if option.text == code_name:
                    option.click()
            helpers.driver.find_element_by_xpath('//*[@id="globalMenuInfo"]/div/div/ul/li/div/form/input[3]').click()
            amount_sold = helpers.driver.find_element_by_xpath('//*[@id="reportTable"]/tbody/tr[last()]/td[2]').text
            results.append([code_name, amount_sold])
            print(code_name + ": " + amount_sold)
        with open(r'C:\Users\rford\Desktop\Richard Ford\Results\Promo_Code_Results.csv', 'w+', newline='', encoding='utf-8') as file:
                writer = helpers.csv.writer(file)
                writer.writerow((['Code', 'Sold']))
                writer.writerows(results)
                print('Promo Codes CSV Created')

    def xlsx_report(self):

        with helpers.pd.ExcelWriter(r'C:\Users\rford\Desktop\Richard Ford\Results\Xlsx_reports\results_{}.xlsx'.format(helpers.currentDate), engine="openpyxl", encoding="utf-8") as xlwriter:# pylint: disable=abstract-class-instantiated
            new_row = []
            df = helpers.pd.read_csv(r'C:\Users\rford\Desktop\Richard Ford\Results\Everyone_results.csv')
            df.to_excel(xlwriter, sheet_name = 'Everyone', index = False)
            df4 = helpers.pd.read_csv(r'C:\Users\rford\Desktop\Richard Ford\Results\Daily Deal_results.csv')
            df4.to_excel(xlwriter, sheet_name = 'Daily Deals', index = False)
            df2 = helpers.pd.read_csv(r'C:\Users\rford\Desktop\Richard Ford\Results\Targeted_results.csv')
            df2.to_excel(xlwriter, sheet_name = 'Targeted', index = False)
            df3 = helpers.pd.read_csv(r'C:\Users\rford\Desktop\Richard Ford\Results\Push Notification_results.csv')
            df3.to_excel(xlwriter, sheet_name = 'Push Notifications', index = False)
            df5 = helpers.pd.read_csv(r'C:\Users\rford\Desktop\Richard Ford\Results\Acquisition_results.csv')
            df5.to_excel(xlwriter, sheet_name = 'Acquisition', index = False)
            df6 = helpers.pd.read_csv(r'C:\Users\rford\Desktop\Richard Ford\Results\Promo_Code_Results.csv')
            df6.to_excel(xlwriter, sheet_name = 'Promo Codes', index = False)
            xlwriter.save()
            print('XLSX Complete')

    def add_prices(self):
        data = helpers.pd.read_csv(r'C:\Users\rford\Desktop\pricing.csv')
        sale_prices = data['Prices'].astype(int).tolist()
        sale_id = input("Enter Sale ID  ")
        helpers.driver.get('#sale={}'.format(sale_id))
        check_boxes = helpers.driver.find_elements_by_class_name('sale_checked')
        input_boxes = helpers.driver.find_elements_by_xpath('//*[contains(@id, "price_")]')
        for check_box in check_boxes:
            check_box.click()
        for input_box in input_boxes:
            input_box.clear()
        for i in range(len(sale_prices)):
            input_boxes[i].send_keys(sale_prices[i])
        save_button = helpers.driver.find_element_by_xpath('//*[@id="update_checked"]')
        save_button.click()
        helpers.WebDriverWait(helpers.driver, 5)
        print('Finished.')

    def delete_items(self):
        ignored_exceptions=(helpers.NoSuchElementException, helpers.StaleElementReferenceException, helpers.TimeoutException)
        df = helpers.pd.read_csv(r'C:\Users\rford\Desktop\items.csv')
        data = df.fillna(0)
        item_number_list = data['Item Numbers'].astype(int).tolist()
        helpers.driver.get("#")
        select = helpers.Select(helpers.driver.find_element_by_xpath('//*[@id="saleTypeId"]'))
        prompt = "Choose Sale Type:\n\t1: Email Special\n\t2: Catalog Sale\n"
        helpers.WebDriverWait(helpers.driver, 10)
        while True:
            try:
                sale_type = int(input(prompt))
                if sale_type < 1 or sale_type > 2:   
                    raise ValueError
                break
            except ValueError:
                prompt = "Please enter 1 or 2:\n> "
        if sale_type == 1:
            select.select_by_value('1')
        else:
            select.select_by_value('2')
        helpers.WebDriverWait(helpers.driver, 15)
        sale_id = input('Please enter Sale ID: ')
        helpers.WebDriverWait(helpers.driver, 20)
        helpers.driver.find_element_by_xpath('//*[@id="saleId"]/option[@value={}]'.format(sale_id)).click()
        for item_number in item_number_list:
            try:
                delete_item_id = "deleteSelectedItem_{}".format(item_number)
                helpers.WebDriverWait(helpers.driver, 20, ignored_exceptions=ignored_exceptions).until(helpers.expected_conditions.presence_of_element_located((helpers.By.ID, delete_item_id)))
                item_to_delete = helpers.driver.find_element_by_xpath('//*[@id="deleteSelectedItem_{}"]'.format(item_number))
                item_to_delete.location_once_scrolled_into_view
                helpers.WebDriverWait(helpers.driver, 10)
                item_to_delete.click()
                helpers.WebDriverWait(helpers.driver, 10)
                print(str(item_number) + " has been deleted from sale")
                helpers.WebDriverWait(helpers.driver, 10)
            except (TimeoutException, NoSuchElementException) as e:
                print("Timed out while searching for item {}").format(item_number)
                continue
        helpers.WebDriverWait(helpers.driver, 5)
        save_sale_id = 'saveItemList'
        save_sale_items = helpers.WebDriverWait(helpers.driver, 10, ignored_exceptions=ignored_exceptions).until(helpers.expected_conditions.presence_of_element_located((helpers.By.NAME, save_sale_id)))
        save_sale_items.click()
        helpers.WebDriverWait(helpers.driver, 10)
        print('Complete. All Items Deleted From Sale')
        helpers.WebDriverWait(helpers.driver, 5)  
        helpers.driver.quit()

    def acquisition_sale(self):
        #set data frame and make column list
            df = helpers.pd.read_csv(r'C:\Users\rford\Desktop\acquisition_info.csv')
            #Parse to Text
            data = df.fillna(0)
            #set ids from each column list
            category = data['Category'].astype(str).tolist()
            item = data['Item'].astype(int).tolist()
            bonus = data['Bonus'].astype(int).tolist()
            expiration = data['Expiration'].astype(str).tolist()
            code = data['Code'].astype(str).tolist()
            for x in range(len(df)):
                #get saleManager.php
                helpers.driver.get("#")
                select = helpers.Select(helpers.driver.find_element_by_xpath('//*[@id="saleTypeId"]'))
                helpers.WebDriverWait(helpers.driver, 10)
                #select Catalog Sales
                select = helpers.Select(helpers.driver.find_element_by_xpath('//*[@id="saleTypeId"]'))
                select.select_by_value('2')
                helpers.WebDriverWait(helpers.driver, 10)
                #check 'Either' radio button on Currently Active
                helpers.driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/form[1]/div/ul/li[2]/input[3]').click()
                #check 'Either' radio button on Sold Online
                helpers.driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/form[1]/div/ul/li[1]/input[3]').click()
                #check 'Either' radio button on Sold to Customers
                helpers.driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/form[1]/div/ul/li[3]/input[3]').click()
                #check 'Either' radio button on Sales Taxable
                helpers.driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/form[1]/div/ul/li[4]/input[3]').click()
                #wait
                helpers.WebDriverWait(helpers.driver, 1)
                #wait
                helpers.WebDriverWait(helpers.driver, 10)
                ignored_exceptions=(helpers.NoSuchElementException, helpers.StaleElementReferenceException)
                helpers.driver.find_element_by_xpath('//*[@id="choosSaleTypeForm"]/div/ul/li[2]/input').click()
                helpers.WebDriverWait(helpers.driver, 10)
                subject = helpers.WebDriverWait(helpers.driver, 10, ignored_exceptions=ignored_exceptions).until(helpers.expected_conditions.presence_of_element_located((helpers.By.ID, 'subject')))
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.driver.find_element_by_xpath('//*[@id="islive"]').click()
                helpers.driver.find_element_by_xpath('//*[@id="is_targeted"]').click()
                helpers.driver.find_element_by_xpath('//*[@id="hasexclusions"]').click()
                subject.send_keys(category[x] + " 90+ Rated 5-Pack & Cutter Only $15!")
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.driver.find_element_by_xpath('//*[@id="expireDateTime"]').clear()
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.driver.find_element_by_xpath('//*[@id="limitamt"]').send_keys('1')
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.driver.find_element_by_xpath('//*[@id="isfreeshipping"]').click()
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.driver.find_element_by_xpath('//*[@id="expireDateTime"]').send_keys(expiration[x])
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.driver.find_element_by_xpath('//*[@id="keycode"]').clear()
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.driver.find_element_by_xpath('//*[@id="keycode"]').send_keys(code[x])
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.WebDriverWait(helpers.driver, 50)
                #Set save sale variable
                helpers.WebDriverWait(helpers.driver, 10, ignored_exceptions=ignored_exceptions).until(helpers.expected_conditions.presence_of_element_located((helpers.By.ID, 'editSaleForm')))
                save_sale = helpers.driver.find_element_by_xpath('//*[@id="editSaleForm"]/div/div/input')
                save_sale.click()
                helpers.WebDriverWait(helpers.driver, 10)
                #delete items showing from previous sale
                helpers.driver.find_element_by_xpath('//*[@id="regsearch"]/form[2]/div/ul/li[4]/input').click()
                helpers.WebDriverWait(helpers.driver, 10)
                #add Item
                helpers.driver.find_element_by_xpath('//*[@name="isInStock"]').click()
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.driver.find_element_by_xpath('//*[@id="name"]').clear()
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.driver.find_element_by_xpath('//*[@id="name"]').send_keys(item[x])
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.driver.find_element_by_xpath('//*[@id="searchinputs"]/div/div[2]/div[3]/input[3]').submit()
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.WebDriverWait(helpers.driver, 10)

                add_to_list_id = 'addToList_{}'.format(item[x])
                helpers.WebDriverWait(helpers.driver, 50)
                ignored_exceptions=(helpers.NoSuchElementException, helpers.StaleElementReferenceException, helpers.TimeoutException)
                helpers.WebDriverWait(helpers.driver, 50)
                add_to_list = helpers.WebDriverWait(helpers.driver, 10, ignored_exceptions=ignored_exceptions).until(helpers.expected_conditions.presence_of_element_located((helpers.By.ID, add_to_list_id)))
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.WebDriverWait(helpers.driver, 30)
                add_to_list.click()
                save_sale_id = 'saveItemList'
                helpers.WebDriverWait(helpers.driver, 10, ignored_exceptions=ignored_exceptions).until(helpers.expected_conditions.presence_of_element_located((helpers.By.NAME, save_sale_id)))
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.WebDriverWait(helpers.driver, 30)
                helpers.WebDriverWait(helpers.driver, 100)
                helpers.driver.find_element_by_xpath('//*[@id="itemButtonForm"]/div/div/input').click()
                helpers.WebDriverWait(helpers.driver, 100)
                helpers.driver.find_element_by_xpath('//*[@id="openAll"]').click()
                helpers.WebDriverWait(helpers.driver, 10, ignored_exceptions=ignored_exceptions).until(helpers.expected_conditions.presence_of_element_located((helpers.By.NAME, save_sale_id)))
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.driver.find_element_by_xpath('//*[@id="editItemForm_{}"]/div/table/tbody/tr[3]/td[2]/input'.format(item[x])).send_keys('15')
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.WebDriverWait(helpers.driver, 20)
                helpers.driver.find_element_by_xpath('//*[@id="itemButtonForm"]/div/div/input').click()
                helpers.driver.find_element_by_xpath('//*[@id="isfreeshipsale_{}'.format(item[x])).click()
                print('Item Added and Priced')
                #Add Bonus
                helpers.driver.find_element_by_xpath('//*[@name="isInStock"]').click()
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.driver.find_element_by_xpath('//*[@id="name"]').clear()
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.driver.find_element_by_xpath('//*[@id="name"]').send_keys(bonus[x])
                helpers.WebDriverWait(helpers.driver, 10)
                helpers.driver.find_element_by_xpath('//*[@id="searchinputs"]/div/div[2]/div[3]/input[3]').submit()
                helpers.WebDriverWait(helpers.driver, 10)
                add_to_item_id = 'addToItem_{}'.format(bonus[x])
                ignored_exceptions=(helpers.NoSuchElementException, helpers.StaleElementReferenceException, helpers.TimeoutException)
                add_to_item = helpers.WebDriverWait(helpers.driver, 10, ignored_exceptions=ignored_exceptions).until(helpers.expected_conditions.presence_of_element_located((helpers.By.ID, add_to_item_id)))
                add_to_item.click()
                helpers.WebDriverWait(helpers.driver, 5)
                print('Bonus {} has been added to Item!'.format(bonus[x]))
               
                helpers.WebDriverWait(helpers.driver, 50)
                # try:
                #     helpers.driver.find_element_by_xpath('//*[@id="editItemForm_{}"]/div/table/tbody/tr[3]/td[2]/input'.format(item[x])).clear()
                # except NoSuchElementException:
                #     pass
                # editItemForm = 'editItemForm_{}'.format(item[x])
                # helpers.WebDriverWait(helpers.driver, 50, ignored_exceptions=ignored_exceptions).until(helpers.expected_conditions.presence_of_element_located((helpers.By.ID, editItemForm)))
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.WebDriverWait(helpers.driver, 30)
                helpers.WebDriverWait(helpers.driver, 50)
                helpers.WebDriverWait(helpers.driver, 30)
                # helpers.driver.find_element_by_xpath('//*[@id="editItemForm_{}"]/div/table/tbody/tr[3]/td[2]/input'.format(item[x])).send_keys('15.00')
                helpers.WebDriverWait(helpers.driver, 10)
               
                helpers.WebDriverWait(helpers.driver, 20)
                
    def get_item_info(self):
        while True:
            item_id = input("Please enter an item number:  ")
            item_results = []
            #set data frame and make column list
            #get saleManager.php
            helpers.WebDriverWait(helpers.driver, 1)  
            #Navigate to item    
            helpers.driver.get("###area=general&id={}".format(item_id))
            helpers.WebDriverWait(helpers.driver,10)
            try:
                #Click 'Yes' on 'Are you sure you want to continue' view
                helpers.driver.find_element_by_css_selector('#form1 > div > input[type=submit]:nth-child(2)').click()
                helpers.WebDriverWait(helpers.driver, 5)
            except helpers.NoSuchElementException:
                pass
            #Get Name
            try:
                name = helpers.driver.find_element_by_xpath('//*[@id="form1"]/div/table/tbody/tr[1]/td[1]/textarea').text
            except helpers.NoSuchElementException:
                print("Unable to find info. Check item number..")
                break
            #Get Quick Book Name
            try:
                qb_name = helpers.driver.find_element_by_name('items[qbname]').get_attribute('value') or " N/A"
            except helpers.NoSuchElementException:
                print("Unable to find info. Check item number..")
                break
            # Get Inventory availability
            qty_available = helpers.driver.find_element_by_xpath('/html/body/form/div/table/tbody/tr[2]/td[1]/b').text[-5:]
            #Parse qty_available to pull only integers
            available = ''.join(filter(lambda i: i.isdigit(), qty_available))
            # Get MSRP
            msrp = helpers.driver.find_element_by_name('items[retail]').get_attribute('value') or " N/A "
            # Get cost depending on what type of Element displays it
            try:
                cost = helpers.driver.find_element_by_name('items[cost]').get_attribute('value') or " N/A "
            except helpers.NoSuchElementException:
                cost = helpers.driver.find_element_by_xpath('//*[@id="form1"]/div/table/tbody/tr[2]/td[3]/table/tbody/tr[4]/td[2]').text or " N/A "
            except helpers.NoSuchElementException:
                cost = helpers.driver.find_element_by_xpath('//*[@id="form1"]/div/table/tbody/tr[2]/td[3]/table/tbody/tr[4]/td[2]/input').text or " N/A "
            #Get FSP
            fsp =  helpers.driver.find_element_by_name('items[salecost]').get_attribute('value') or " N/A "
            #Get Price
            price = helpers.driver.find_element_by_name('items[price]').get_attribute('value') or " N/A "
            # Grab list of  Length Options & Set Length
            _length_options = helpers.Select(helpers.driver.find_element_by_name('items[clen]'))
            length = _length_options.first_selected_option.text
            # Grab list of  Gauge Options & Set Gauge
            gauge_length_options = helpers.Select(helpers.driver.find_element_by_name('items[cdiam]'))
            gauge = gauge_length_options.first_selected_option.text
            # Grab list of  Packaging Types & Set Type
            packaging_type_options = helpers.Select(helpers.driver.find_element_by_name('items[cpack]'))
            packaging_type = packaging_type_options.first_selected_option.text
            # Grab list of  Box Count & Set Count
            stick_count_options = helpers.Select(helpers.driver.find_element_by_name('items[ccount]'))
            stick_count = stick_count_options.first_selected_option.text
            #Grab list of Availabilities & Set Availability
            availability_options = helpers.Select(helpers.driver.find_element_by_name('items[availid]'))
            availability = availability_options.first_selected_option.text
            #Add data to results list
            item_results.append([item_id, name, qb_name, available, cost, price, msrp, fsp, length, gauge, packaging_type, stick_count, availability])
            #print info gathered into Terminal
            print("Item ID: " + str(item_id) + "\n" + "Description: " + str(name) + "\n" + "Quickbook Name: " + str(qb_name) + "\n" + "Available: " + str(available) + "\n" + "Cost: " + str(cost) + "     " + "Retail: "  + str(price) + "      MSRP: " + str(msrp) +  " \n" + "Length: " + str(length) + "\n" + "Gauge: " + str(gauge) + "\n" + "Packaging Type: " + str(packaging_type) + "\n" + "Stick Count: " + str(stick_count))
            helpers.driver.quit()
            input("Press 'Y' to look up another item. Press 'Q' to quit  ")
            if input == "Y" or "y":
                continue
            else:
                break

    def get_sale_info(self):
        while True:
            form_code = int(input("Enter 1: Email Special   2: Catalog Sale\n"))
            if form_code == 1 or "1":
                sales_type = "Email Special"
            if form_code == 2 or "2":
                sales_type = "Catalog Sale"
            elif form_code >= 7 or form_code <= 0:
                print("Incorrect Input!")
            sale_id = input("Enter Sale ID:  ")
            helpers.WebDriverWait(helpers.driver, 10)  
            #Navigate to item    
            helpers.driver.get('#')
            helpers.WebDriverWait(helpers.driver,10)
            #Grab sale option for each form id and sale id
            try:
                helpers.WebDriverWait(helpers.driver,10)
                helpers.driver.find_element_by_xpath('/html/body/form[{}]/div/select/option[@value={}]'.format(form_code, sale_id)).click()
            except NoSuchElementException:
                print('Incorrect ID, Sale not Found')
                break
            #Parse date created from title
            date_created = helpers.driver.find_element_by_xpath('/html/body/form[{}]/div/select/option[@value={}]'.format(form_code, sale_id)).text[:10]
            #Parse expiration date created from title
            exp_date = helpers.driver.find_element_by_xpath('/html/body/form[{}]/div/select/option[@value={}]'.format(form_code, sale_id)).text[-19:-9]
            #Parse Sale Code from title
            sale_code = helpers.driver.find_element_by_xpath('/html/body/form[{}]/div/select/option[@value={}]'.format(form_code, sale_id)).text[11:17]
            #Submit form
            helpers.driver.find_element_by_xpath('/html/body/form[{}]/div/input[1]'.format(form_code)).submit()
            helpers.WebDriverWait(helpers.driver, 1)
            #Get Sale title from table
            title = helpers.driver.find_element_by_xpath('/html/body/h2[2]').text or "N/A"
            #Get total sold from table
            sold = helpers.driver.find_element_by_xpath('/html/body/table[1]/tbody/tr[last()]/td[4]').text or "0"
            #add results to list
            print("Title: " + title + "\n" + "Sold: " + sold + "\n" + "Sale ID: " + sale_id + "\n" + "Created: " + date_created + "      Expiration: " +  exp_date + "\n" + "Category: " + sales_type +"      Code: " + sale_code)
            input("Press 'Y' to look up another item. Press 'Q' to quit  ")
            if input == "Q" or "q":
                break
            else:
                continue
        
       
#Create instance of Sale
sales = Sales()


#################################################################################################################################################################################################################
# Terminal Logic
while True:
    try:
        answer = int(input("Choose function: \n1: Make a Sale \n2: Make Sales Report \n3: Add Pricing to Sale\n4: Delete Items from Sale\n5: Look up item info\n6: Look Up Sale Results\n\n\n"))
        if answer == 1:
            sales.make_sale()
            continue
        elif answer == 2:
            sales.get_report_data()
            sales.coupon_results()
            sales.xlsx_report()
            continue
        elif answer == 3:
            sales.add_prices()
            continue
        elif answer == 4:
            sales.delete_items()
            continue
        elif answer == 5:
            sales.get_item_info()
            continue
        elif answer == 6:
            sales.get_sale_info()
            continue
        elif answer > 6 or answer <= 0:
            print("Please Enter a number from the menu above....\n")
    except ValueError:
        print("Error Occured\n")
        print("\n")
       