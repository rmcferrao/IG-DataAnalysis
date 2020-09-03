from IGScrapper import *
import json
from selenium import webdriver
from os.path import dirname, abspath, join

if __name__ == '__main__':

    FILE_PATH = dirname(abspath(__file__))
    ROOT_FOLDER_PATH = dirname(dirname(FILE_PATH))
    webDriver = join(ROOT_FOLDER_PATH, 'chromedriver')
    print(webDriver)

    igPageData = {}
    
    # morganfreeman, gretathunberg, luizaquental
    igUser = 'neymarjr'
    visible = False  #If visible is True user must not resize the webpage

    mainIgPage = f"https://www.instagram.com/{igUser}/?hl=en"

    options = webdriver.ChromeOptions()
    options.add_argument("window-size=1920x1080")
    options.add_argument("disable-gpu")
    options.add_argument("--lang=en")

    if not visible:
        options.add_argument("--headless")

    driver = webdriver.Chrome(executable_path=webDriver, chrome_options=options)
    driver.get(mainIgPage)

    igProfile = IGProfile(driver)

    mainDict = igProfile.getMetaMainPage()
    igPageData['main-data'] = mainDict

    igPageData['main-data']['is-verified'] = igProfile.isVerified()
    igPageData['main-data']['posts'] = igProfile.getTotalNumberPosts()
    igPageData['main-data']['followers'] = igProfile.getTotalNumberFollowers()
    igPageData['main-data']['following'] = igProfile.getTotalNumberFollowing()

    nScrollTimes = 200
    iScroll = 0
    iPost = 1

    postLinksDict = {}
    while iScroll < nScrollTimes: 
        try:
            igProfile.scrollDown()
        except:
            break

        postLinks = igProfile.getPostLinks()
        iScroll += 1
        print(f'Scrolling down ... {iScroll} times -----------------------')

        for postLink in postLinks:
            auxPostLinks = list(postLinksDict.values())
            if iScroll > 1:
                auxPostLinks =  auxPostLinks[-36:]

            if postLink not in auxPostLinks:
                postLinksDict[str(iPost)] = postLink
                iPost += 1
            
    print(f'{len(postLinksDict.values())} Post Links Scrapped -------------------------')
    igPageData['post-links'] = postLinksDict

    igPageData['post-data'] = {}

    postMetaProperties = ['og:image', 'og:type', 'og:title', 'og:description']

    for postNumber, postUrl in igPageData['post-links'].items():
        print(f'Post{postNumber}----------------------')
        driver.get(postUrl)

        igPost = IGPost(driver)
        metaPostPage = igPost.getMetaPostPage(postMetaProperties)
        metaPostPage['date-time'] = igPost.getPostDate()
        metaPostPage['views'] = igPost.getPostViews()
        metaPostPage['likes'] = igPost.getPostLikes()
        metaPostPage['video-link'] = igPost.getVideoLink()
        metaPostPage['photos-src-alt'] = igPost.getPhotosSrcAlt()
        metaPostPage['location'] = igPost.getPostLocation()

        igPageData['post-data'][postNumber] = metaPostPage

    with open(join(ROOT_FOLDER_PATH, 'data', f'{igUser}-raw.json'), 'w', encoding='utf8') as jsonfile:
        json.dump(igPageData, jsonfile, indent=4, ensure_ascii=False)
        
    igPost.close()