'''
[] Ability to track what individual user has viewed
[] Online version: meaningless points for creating tags (which are upvoted)
[] Ability to track what has been viewed (so people will see new things)
[] Image submission: hash collision -- present choice to submit/reject to user.
'''


#=== Build Notes:
'''Build this in Python 3.
    Build GUI in HTML/Javascript.
'''

#=== Concept:
'''Danboru, but with additional:
(1) Desktop support
    Ability to easily turn it into an online version
    Ability to merge your database into an existing online or other desktop version.
(2) User craft collections.
(3) Meta-tag - tags grouping tags. (~mind-mapping)
(4) Sub-tag - non-overlapping tags nestled within other tags (tits: small, medium, large)
(5) Search results - group/cluster based on tag similarity (sub-tags?)
(6) Better Booleans: beyond 'yes' 'no': maybe, should have, should not have, must have, must not have
(7) Browser App: allow you to download a picture while adding tags (and depositing it into the system).
        Ways to control default tags. Keyboard shortcuts for tags. 
        And single button download. (mouseover, press SHIFT+D or similar).
'''

#=== Minimum Requirements:
'''
(1) Basic tags
(2) Add image records to SQL-lite database.
(3) Images stored in a folder, no name changes.
(4) Basic GUI to:
        Add tags to 'cloud'
        Apply a tag to image.
        Search tags.
        List images: paging of thumbnails.
            Click for a larger popup.
'''


#Extract image upload from server.py
    #Decouple from web.input (the result of the form, from web.py)
#Setup a join table

#Do code portion of tag uploading
#Fuck with web portion of tag uploading
#Create join table
#Function to upload whole folder

#tag functions - in Python or in SQL?
