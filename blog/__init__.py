from blog.xmlrpc import *

xmlrpcdispatcher.register_function(blogger_getUsersBlogs, 'blogger.getUsersBlogs')
xmlrpcdispatcher.register_function(metaWeblog_getCategories, 'metaWeblog.getCategories')
xmlrpcdispatcher.register_function(metaWeblog_newPost, 'metaWeblog.newPost')
xmlrpcdispatcher.register_function(metaWeblog_editPost, 'metaWeblog.editPost')
xmlrpcdispatcher.register_function(metaWeblog_getPost, 'metaWeblog.getPost')
xmlrpcdispatcher.register_function(metaWeblog_getRecentPosts, 'metaWeblog.getRecentPosts')
xmlrpcdispatcher.register_function(ping_func, 'pingback.ping')

