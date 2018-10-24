"""
>>> from blog.utils import autocard
>>> content = "<card>Scryb Sprites</card>"
>>> autocard(content)
'<a href="http://magiccards.info/autocard.php?card=Scryb Sprites">Scryb Sprites</a>'
>>> content = "<deck>Lands\\n1 Mountain\\n1 Swamp\\n99 Forest</deck>"
>>> autocard(content)
'<div class=\\'decklist\\'><ul class=\\'decklist_group\\'></ul><ul class=\\'decklist_group\\'><li class=\\'header\\'>Lands</li>\\n<li>1 <a href="http://magiccards.info/autocard.php?card=Mountain">Mountain</a></li>\\n<li>1 <a href="http://magiccards.info/autocard.php?card=Swamp">Swamp</a></li>\\n<li>99 <a href="http://magiccards.info/autocard.php?card=Forest">Forest</a></li>\\n</ul><div style=\\'clear:both\\'></div></div>'
""" 