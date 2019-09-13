from selenium import webdriver;from selenium.webdriver.chrome.options import Options;import time;from selenium.webdriver.common.action_chains import ActionChains;from selenium.common.exceptions import * ; import mysql.connector ; import re



class Amazon_scrape():
    def __init__(self):
        self.links=[]
    def scrape_init(self,url='https://www.amazon.com/s?k=contour+pillow&rh=n%3A1055398%2Cn%3A1199122&dc&qid=1568083351&rnid=2941120011&ref=sr_nr_n_2'):
        option = webdriver.ChromeOptions()

        # 无头模式
        option.add_argument('--headless')
        option.add_argument('start-maximized')


        # 更换头部
        option.add_argument(
        'user-agent="Mozilla/5.0(Macintosh;IntelMacOSX10_9_3)AppleWebKit/537.36(KHTML,likeGecko)Chrome/35.0.1916.47Safari/537.36"')

        # 添加历史cookie
        option.add_argument("--user-data-dir=C:\\Users\\肖洪才\\AppData\\Local\\Google\\Chrome\\User Data1");option.add_argument('disable-infobars')

        self.browser = webdriver.Chrome(chrome_options=option,
                                   executable_path=r'C:\Users\肖洪才\AppData\Local\Programs\Python\Python37-32\Scripts\chromedriver.exe')


        self.browser.get(url) ; time.sleep(1) ; self.browser.implicitly_wait(5)


    def flip_page(self):
        next_page_element=self.browser.find_element_by_css_selector('#search > div.sg-row > div.sg-col-20-of-24.sg-col-28-of-32.sg-col-16-of-20.sg-col.s-right-column.sg-col-32-of-36.sg-col-8-of-12.sg-col-12-of-16.sg-col-24-of-28 > div > span:nth-child(9) > div > div > div > ul > li.a-last > a')
        ActionChains(self.browser).move_to_element(next_page_element).perform() ; next_page_element.click()



    def insert_current(self): # insert  current page whole links into links list
                self.links.extend([i.get_attribute('href') for i in self.elements])




    def engine_1_scrape_whole_product_links(self):
        def save_into_mysql(list):
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                database="sys"
            )

            mycursor = mydb.cursor()

            for i in self.links:
                sql='insert into amazon (Link) values (%s)'
                val=(i,) ; print('link tuple',val)


                mycursor.execute(sql,val)

            mydb.commit() ; print('Whole save process finished')



        #fetch maximum page
        max_page=self.browser.find_element_by_css_selector('#search > div.sg-row > div.sg-col-20-of-24.sg-col-28-of-32.sg-col-16-of-20.sg-col.s-right-column.sg-col-32-of-36.sg-col-8-of-12.sg-col-12-of-16.sg-col-24-of-28 > div > span:nth-child(9) > div > div > div > ul > li:nth-child(6)').text
        print('max_page:',max_page)


        for i in range(int(max_page)):
            try:


                #sum the whole link number
                self.elements=self.browser.find_elements_by_css_selector('div[class="s-result-list s-search-results sg-row"] div[class="sg-col-inner"] a[class="a-link-normal a-text-normal"]') ; print(f'{len(self.elements)} links has been inserted')



                self.insert_current() ; print(f'Scraping {i+1} page insert success') ; print(self.links)


                self.flip_page()

            except NoSuchElementException as e:

                pass


        #write into txt
        save_into_mysql(self.links)


    # The connection of seperate engine
    def browser_quit(self):
        self.browser.quit() ; print('Browse has quitted')

    '''----------------------engine_2----------------------------------'''

    #The main part of engine 2
    def get_target_infos_of_link_and_save(self):

        def save_into_mysql(product_title,price,rank_data,positive_review_amount,negative_review_amount,negative_review_title):
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                database="sys"
            )

            mycursor = mydb.cursor()

            sql = 'update amazon set product_title=%s,price=%s,rank_data=%s,positive_review_amount=%s,negative_review_amount=%s,negative_review_title=%s  where ID=(%s)'
            val = (
            product_title, price, rank_data, positive_review_amount, negative_review_amount, negative_review_title, self.ID)

            mycursor.execute(sql, val)

            mydb.commit()

        comment = []
        browser=self.browser

        #Why add Try? cause some page doesn't have such element,but not all element
        try:
            product_title = browser.find_element_by_css_selector('span[id="productTitle"]').text
            print('scrape product title OK :', product_title)
        except:
            print('scrape product title failed')
            product_title=0
            pass

        try:
            price = browser.find_element_by_css_selector('span[id="priceblock_ourprice"]').text[1:]
            print('scrape product price OK :', price)
        except:
            try:
                price = browser.find_element_by_css_selector('td.comparison_baseitem_column > span > span:nth-child(2) > span.a-price-whole').text
            except:
                print('scrape product price failed')


                price = 0
                pass

        try:
            rank_data = browser.find_element_by_css_selector(
                '#productDetails_detailBullets_sections1 > tbody > tr:last-child > td > span').text
            print('scrape product rank OK :', rank_data)
        except:
            print('scrape product rank failed')

            rank_data=0
            pass

        # middle save process for exception,if the comment scraping is failed,you at least save above infos rather than Nothing
        negative_review_title = 0
        positive_review_amount = 0
        negative_review_amount = 0
        save_into_mysql(product_title, price, rank_data, positive_review_amount, negative_review_amount,
                        negative_review_title)
        print('Middle save success')




        # move the target for clicking review page (this click action may not always success ,causue some page doesn't have it '
        ActionChains(browser).move_to_element(browser.find_element_by_css_selector(
            '#cr-dp-summarization-attributes > div.a-row.a-spacing-medium > span')).perform()




        # click review page

        browser.find_element_by_css_selector(
            '#histogramTable > tbody > tr:nth-child(1) > td.a-span10 > a > div > div').click()
        print('click review page link OK')




        # wait
        browser.implicitly_wait(10)

        # scrape positive review amount
        positive_review_amount = re.findall('\d+,*\d+', browser.find_element_by_css_selector(
            'div[class="a-column a-span6 view-point-review positive-review"] div.a-expander-content.a-expander-partial-collapse-content > div:nth-child(2) > span > a').text)[
            0]
        print(f'scrape positive amount OK {positive_review_amount}')

        # scrape negative review amount
        negative_review_amount = re.findall('\d+', browser.find_element_by_css_selector(
            'div[class="a-column a-span6 view-point-review critical-review a-span-last"] div.a-expander-content.a-expander-partial-collapse-content > div:nth-child(2) > span > a').text)[
            0]
        print(f'scrape negative amount OK {negative_review_amount}')


        # save positive_review_amount and  negative_review_amount
        negative_review_title = 0

        save_into_mysql(product_title, price, rank_data, positive_review_amount, negative_review_amount,
                        negative_review_title)
        print('Middle_2 save success')


        # click into negative page
        browser.find_element_by_css_selector(
            'div.a-expander-content.a-expander-partial-collapse-content > div:nth-child(2) > span > a[data-reftag="cm_cr_arp_d_viewpnt_rgt"]').click()
        print('click negative link OK')
        browser.implicitly_wait(10)
        time.sleep(1)



        # scrape inner negative review
        while 1:

            try:

                try:
                    # scrape all current page comment
                    comment.extend([i.text for i in browser.find_elements_by_css_selector(
                        'div[id="cm_cr-review_list"] a[data-hook="review-title"] span')])
                    print(f'comment amount:{len(comment)}  :', comment)
                except:
                    # re-scrape all current page comment
                    comment.extend([i.text for i in browser.find_elements_by_css_selector(
                        'div[id="cm_cr-review_list"] a[data-hook="review-title"] span')])
                    print(f'comment amount:{len(comment)}  :', comment)

                # detect if is last page ___double try
                try:
                    negative_review_situation = browser.find_element_by_css_selector(
                        '#filter-info-section > span:nth-child(1)').text
                    current_last_comment = re.findall('-\d+', negative_review_situation)[0][1:]
                    print(current_last_comment)
                    target_last_comment = re.findall('of \d+', negative_review_situation)[0].split(' ')[1]
                    print(target_last_comment)
                    if int(target_last_comment)>=100:
                        target_last_comment=str(100)
                    if current_last_comment == target_last_comment:
                        break
                except:
                    negative_review_situation = browser.find_element_by_css_selector(
                        '#filter-info-section > span:nth-child(1)').text
                    current_last_comment = re.findall('-\d+', negative_review_situation)[0][1:]
                    print(current_last_comment)
                    target_last_comment = re.findall('of \d+', negative_review_situation)[0].split(' ')[1]
                    print(target_last_comment)
                    if target_last_comment >= 100:
                        target_last_comment = 100
                    if current_last_comment == target_last_comment:
                        break

                # move to next page button and click it
                ActionChains(browser).move_to_element(
                    browser.find_element_by_css_selector('#navBackToTop > div > span')).perform()
                browser.find_element_by_css_selector('#cm_cr-pagination_bar > ul > li.a-last > a').click() ; print('click bad review inner next page OK')

                time.sleep(1)
            except Exception as e:

                print('Error:', e) ; break

        print('the whole amount of comment:', len(comment), '  :      ', comment)

        #Turn your comment from list formation to str,so that you can directly obeserve in your final database
        negative_review_title = '\n\n'.join(comment)


        #final save process ,cause you have scrape your comment content
        save_into_mysql(product_title, price, rank_data, positive_review_amount, negative_review_amount,negative_review_title)
        print('Final save success')


    #After you have scrape all links ,then you need to scrape each of their infos
    def engine_2_get_spare_infos(self):

        #initial links containter for Mysql
        self.ID_and_links=[]

        #The single target link for scraping
        self.scraped_link=''

        #Fetch all links from mysql
        def fetch_mysql():


            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                database="sys"
            )

            mycursor = mydb.cursor()

            mycursor.execute("SELECT ID,Link FROM amazon where product_title is not null")

            self.ID_and_links= mycursor.fetchall()

        count=0

        fetch_mysql()

        #Iterate whole links for singlely processing
        for x in self.ID_and_links:
            self.ID=x[0]
            self.scraped_link=x[1]



            #This count means your scrape page times ,first scrape means count=1 and so on
            count+=1

            print('Processing ',count,' link....:',self.scraped_link)
            start_time=time.time()

            #open up that single link
            try:
                self.browser.get(self.scraped_link)
                self.get_target_infos_of_link_and_save() ; print(self.scraped_link,'has been scraped')

                end_time=time.time() ; print('Costing :',end_time-start_time,' seconds')

            except Exception as e:
                print('Some thing goes wrong',e)
                continue


if __name__ == '__main__':
    amz=Amazon_scrape() ; amz.scrape_init()
    # amz.engine_1_scrape_whole_product_links()
    # amz.browser_quit()
    amz.engine_2_get_spare_infos()

