import time
import unicodedata

def getMetaContents(driver, metaProperties : list):
    metaElements = driver.find_elements_by_xpath('/html/head/meta')
    metaContent_dict = {}

    for metaElement in metaElements:
        metaProperty = metaElement.get_attribute('property')
        metaContent = metaElement.get_attribute('content')

        if metaProperty in metaProperties:
            metaContent_dict[metaProperty] = metaContent

    return metaContent_dict

def is_profile(func):
    def _decorator(self, *args, **kwargs):
        metaElement = args[0].find_element_by_xpath('/html/head')
        pageType = metaElement.find_element_by_xpath('//meta[@property="og:type"]').get_attribute('content')

        if 'profile' in pageType:
            return func(self, *args, **kwargs)

        else:
            raise EnvironmentError("This page is not the Instagram profile page")

    return _decorator

def is_post(func):
    def _decorator(self, *args, **kwargs):
        metaElement = args[0].find_element_by_xpath('/html/head')
        pageType = metaElement.find_element_by_xpath('//meta[@property="og:type"]').get_attribute('content')

        if not 'profile' in pageType:
            return func(self, *args, **kwargs)

        else:
            raise EnvironmentError("This page is not the Instagram post page")

    return _decorator

def info_exists(func):
    def _decorator(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except:
            # print(f'Info gathered by function {func.__name__} does not exists')
            return False

    return _decorator

def normalizeText(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'replace')

class IGProfile:

    SCROLL_PAUSE_TIME = 2

    @is_profile
    def __init__(self, driver):
        self.driver = driver
        self.subHeaderDiv = self.driver.find_element_by_css_selector('.zwlfE')
        self.postsFollewrsFollowingDiv = self.subHeaderDiv.find_element_by_css_selector('.k9GMp ')

        self.mainSection = self.driver.find_element_by_css_selector('._2z6nI ')
        
    def isVerified(self):
        try:
            self.subHeaderDiv.find_element_by_css_selector('.mTLOB.Szr5J.coreSpriteVerifiedBadge ')
            return True
        except:
            return False

    def getTotalNumberPosts(self):
        nPosts = self.postsFollewrsFollowingDiv.find_element_by_xpath('li[1]/a/span').text
        return nPosts

    def getTotalNumberFollowers(self):
        nFollowers = self.postsFollewrsFollowingDiv.find_element_by_xpath('li[2]/a/span').text
        return nFollowers

    def getTotalNumberFollowing(self):
        nFollowing = self.postsFollewrsFollowingDiv.find_element_by_xpath('li[3]/a/span').text
        return nFollowing

    def getMetaMainPage(self, mainPageMetaProperties = ['og:image', 'og:title', 'og:description', 'og:url', 'og:type']):
        metaContent_dict = getMetaContents(self.driver, mainPageMetaProperties)
        return metaContent_dict

    def scrollDown(self):
        pageHeight = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(IGProfile.SCROLL_PAUSE_TIME)

        newPageHeight = self.driver.execute_script("return document.body.scrollHeight")

        if newPageHeight == pageHeight:
            try:
                self.driver.find_elements_by_css_selector(".tCibT.qq7_A.z4xUb.w5S7h")[0].click()
                time.sleep(IGProfile.SCROLL_PAUSE_TIME)
            except:
                print(f"Reached bottom of the page\n-----------------------------------")
                raise EnvironmentError('No more posts to Scrap')

    def getPostLinks(self):
        postLinks = []

        for imageDiv in self.mainSection.find_elements_by_css_selector('.v1Nh3.kIKUG._bz0w'):
            postLink = imageDiv.find_element_by_tag_name('a').get_attribute('href')
            postLinks.append(postLink)
                
        return postLinks

    def close(self):
        self.driver.close()


class IGPost:

    @is_post
    def __init__(self, driver):
        self.driver = driver
        self.mainArticle = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article')

    @info_exists
    def getPostLocation(self):
        return self.mainArticle.find_element_by_css_selector('.O4GlU').text

    def getMetaPostPage(self, postMetaProperties):
        metaContent_dict = getMetaContents(self.driver, postMetaProperties)
        return metaContent_dict

    @info_exists
    def getPostLikes(self):
        likesDiv = self.mainArticle.find_element_by_css_selector('.Nm9Fw')
        likesText = likesDiv.find_element_by_tag_name('span').text
        return likesText

    @info_exists
    def getVideoLink(self):
        videoElement = self.mainArticle.find_element_by_css_selector('.tWeCl')
        videoSrc = videoElement.get_attribute('src')
        return videoSrc

    @info_exists
    def getPostViews(self):
        viewsSpan = self.mainArticle.find_element_by_css_selector('.vcOH2')
        viewsText = viewsSpan.find_element_by_tag_name('span').text
        return viewsText

    # @info_exists
    def getPostDate(self):
        try:
            return self.mainArticle.find_element_by_css_selector('._1o9PC.Nzb55').get_attribute('datetime')
        except:
            return self.mainArticle.find_element_by_css_selector('.FH9sR.Nzb55').get_attribute('datetime')


    @info_exists
    def getPhotosSrcAlt(self):
        photosElements = self.mainArticle.find_elements_by_css_selector('.FFVAD')

        if not photosElements:
            return IGPost.notFound

        photosAltSrcList = []
        for photoElement in photosElements:
            photoAltSrc = {}
            photoAltSrc['src'] = photoElement.get_attribute('src')
            photoAltSrc['alt'] = photoElement.get_attribute('alt')
            photosAltSrcList.append(photoAltSrc)

        return photosAltSrcList

                
    def close(self):
        self.driver.close()