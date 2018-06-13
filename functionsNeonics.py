# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""
def add_user(u,c, ln=1):
    '''Create the user entity and main attributes
    u: the tweeter user list
    c: the tweeter connexion
    ln : directly linked to neononics (1 : directly published a status with an neonic tag or was mentioned or replied in such tweet(default); 0 : never tweeted about neoncics)
    '''
    c.execute('''INSERT INTO users(id,screen_name,created_at,description,favourites_count,
            followers_count,friends_count,lang,listed_count,
            location,name,statuses_count, linked_neonics)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?) ''', 
          (str(u['id']),u['screen_name'],u['created_at'],u['description'],str(u['favourites_count']),
            str(u['followers_count']),str(u['friends_count']),u['lang'],str(u['listed_count']),
              u['location'],u['name'],str(u['statuses_count']),str(u['ln'])))

def add_status(s,c, ln=1):
    '''Create the status entity, main attributes, hashtags and relative users (autor, replied, mentioned)'''
    c.execute('''
    INSERT INTO 
        statuses(id,created_at,favorite_count,
        lang,retweet_count,source,txt)
    VALUES (?, ?,? ,?  ,? ,? ,?, ?)''', (str(s['id']),s['created_at'],str(s['favorite_count']),
        s['lang'],
        str(s['retweet_count']),
        s['source'], 
        s['text'],
        str(s['ln'])))
    
    #Facultative attributes (None if absent)
    for k in ['in_reply_to_status_id','place','coordinates','in_reply_to_user_id']:
        if s[k] is not None:
            v=(k, str(s[k]), str(s['id']))
            c.execute('''
            UPDATE statuses
            SET %s = ?
            WHERE id = ?''' % k, (str(s[k]), str(s['id'])))
    
    #Facultative attributes (not in s if absent)
    for k in ['scopes','withheld_in_countries','quoted_status_id']:
        if k in s :
            c.execute('''
            UPDATE statuses
            SET %s=?
            WHERE id=?'''% k,(str(s[k]),str(s['id'])))

    #Other entities
    for k in ['retweeted_status','user']:
        if k in s :
            c.execute('''
                UPDATE statuses
                SET %s_id=?
                WHERE id=?''' % k, (str(s[k]['id']),str(s['id'])))

            
            
    ###########################################USERS##############################################
    #add users if not in the database
    #autor
    autor=c.execute("SELECT * FROM users WHERE id=?", (str(s['user']['id']),)).fetchone()
    if autor==None:#if not in the base => add id
        u=twitter_api.users.show(id=str(s['user']['id']))
        add_user(u,c,ln=ln)
    elif ln==1 and autor[-1]==0:#if directly linked to neonics => link it
        c.execute("UPDATE users SET linked_neonics=1 WHERE id={}",(str(autor[0]),)

    #autor of the replied tweet
    if not s['in_reply_to_user_id']==None:
        replied=c.execute("SELECT * FROM users WHERE id=?", (str(s['in_reply_to_user_id']),)).fetchone()
        if replied==None:#if not in the base => add id
            u=twitter_api.users.show(id=str(s['in_reply_to_user_id']))
            add_user(u,c,ln=1)
        elif ln==1 and replied[-1]==0:#if directly linked to neonics => link it
            c.execute("UPDATE users SET linked_neonics=1 WHERE id={}",(str(replied[0]),)
            
        
    #users mentioned        
    for u in s['entities']['user_mentions']:
        if (c.execute('''SELECT * FROM mentions 
                    WHERE status_id = ? AND user_id = ?''', (str(s['id']),str(u['id']))).fetchone())==None:
            #We do not register the multiple mentions of a user in a tweet
            
            mentioned=c.execute('''SELECT * FROM users WHERE id=?''', (str(u['id']),)).fetchone()
            if mentioned==None:#if not in the base => add id
                u=twitter_api.users.show(id=str(u['id']))
                add_user(u,c,ln=1) 
            elif n==1 and mentioned[-1]=0:#if directly linked to neonics => link it
                c.execute("UPDATE users SET linked_neonics=1 WHERE id={}",(str(mentioned[0]),))
            
            #Add the user mentions         
            c.execute('''INSERT INTO mentions(status_id ,user_id)
                        VALUES (?, ?)''', (str(s['id']),str(u['id'])))

    ################################# HASHTAGS #################################################
    for h in s['entities']['hashtags']:
        if (c.execute('''SELECT * FROM tags 
                    WHERE status_id=? AND htg = ?''',(str(s['id']),h['text'].lower())).fetchone())==None:
            #Ajouter le htg 
            c.execute('''INSERT INTO tags(status_id, htg) VALUES (?,?)''',(str(s['id']),h['text'].lower()))
            
#TO DO :
    #Test it
    #Add all users linked with ln = 0