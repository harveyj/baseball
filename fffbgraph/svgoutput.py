#! /usr/bin/env python

import sys
from optparse import OptionParser

BOX_HEIGHT = 20
BOX_VPADDING = 3
BOX_WIDTH = 50
BOX_HPADDING = 2
BOX_VTOTAL = BOX_HEIGHT + BOX_VPADDING
BOX_HTOTAL = BOX_WIDTH + BOX_HPADDING
VMARGIN = 80
HMARGIN = 150
ARROW_WIDTH = 25

class Elem:
  def __init__(self, tagname='g'):
    self.attrs = []
    self.tagname = tagname
    self.elements = []

  def __repr__(self):
    attrstring = ' '.join(['%s="%s"' % x for x in self.attrs])
    child_str = ''.join([str(x) for x in self.elements])
    return '<%s %s>%s</%s>' % (self.tagname, attrstring, 
                               child_str, self.tagname)
  def AddChild(self, elem):
    self.elements.append(elem)

class Document(Elem):
  def __init__(self):
    Elem.__init__(self, tagname="svg")
    self.attrs += [('width', "100%"), ('height', "1300"), 
                   ('xmlns', 'http://www.w3.org/2000/svg'), ('version', '1.1')]

class Rect(Elem):
  def __init__(self, x, y, width=BOX_WIDTH, height=BOX_HEIGHT,
               fill="#cc3333"):
    Elem.__init__(self, tagname="rect")
    self.attrs += [('width', width), ('height', height), 
                   ('fill', fill), ('x', str(x)), ('y', str(y))]

class Polygon(Elem):
  def __init__(self, points, fill='#cc3333'):
    Elem.__init__(self, tagname="polygon")
    self.attrs += [('points', points), ('fill', fill)]

class ContinuedRightBox(Elem):
  def __init__(self, x, y, fill):
    Elem.__init__(self, tagname="g")
    self.AddChild(Rect(x, y, width=BOX_WIDTH-ARROW_WIDTH, fill=fill))
    pt1 = '%i,%i' % (x+BOX_WIDTH,   y+BOX_HEIGHT/2)
    pt2 = '%i,%i' % (x+BOX_WIDTH - ARROW_WIDTH, y)
    pt3 = '%i,%i' % (x+BOX_WIDTH - ARROW_WIDTH, y+BOX_HEIGHT)
    points = '%s %s %s' % (pt1, pt2, pt3)
    self.AddChild(Polygon(points, fill))

class ContinuedLeftBox(Elem):
  def __init__(self, x, y, fill):
    Elem.__init__(self, tagname="g")
    self.AddChild(Rect(x+ARROW_WIDTH, y, width=BOX_WIDTH-ARROW_WIDTH, fill=fill))
    pt1 = '%i,%i' % (x,             y+BOX_HEIGHT/2)
    pt2 = '%i,%i' % (x+ARROW_WIDTH, y)
    pt3 = '%i,%i' % (x+ARROW_WIDTH, y+BOX_HEIGHT)
    points = '%s %s %s' % (pt1, pt2, pt3)
    self.AddChild(Polygon(points, fill=fill))

class Text(Elem):
  def __init__(self, x, y, text="Dummy", family='Helvetica', size=12,
               anchor='middle'):
    Elem.__init__(self, tagname="text")
    self.attrs += [('x', str(x)), ('y', str(y)), ('fill', '#ccc'),
                   ('font-family', family), ('text-anchor', anchor),
                   ('font-size', str(size))]
    self.AddChild(text)

class PlayerGroup(Elem):
  def __init__(self, player, team,
               xloc=HMARGIN, yloc=VMARGIN, 
               year_start=2000, year_end=2009,
               fill_team='#BF0808', fill_not='#dddddd'):
    Elem.__init__(self, tagname='g')
    self.xloc = xloc
    self.yloc = yloc

    self.elements.append(Text(y=self.yloc + BOX_HEIGHT * 0.75, x=self.xloc - BOX_WIDTH/2, 
                              text=player.name, anchor='end'))
    
    # Played before date range.
    if player.min_year() < year_start:
      fill = fill_team if team.team_id in player.years.get(year_start, []) else fill_not
      self.elements.append(ContinuedLeftBox(self.xloc, self.yloc, fill))

    for year in range(year_start, year_end):
      fill = fill_team if team.team_id in player.years.get(year, []) else fill_not
      if year in player.years:
        self.AddBox(year, year_start, fill)

    if player.max_year() > year_end:
      fill = fill_team if team.team_id in player.years.get(year_end, []) else fill_not
      self.elements.append(ContinuedRightBox(
          self.xloc + (year_end - year_start + 1) * BOX_HTOTAL,
          self.yloc, fill))

  def AddBox(self, year, year_start, fill):
    # Transform to zero-based. Leave room for the start arrow.
    y = year - year_start + 1
    self.elements.append(Rect(x=self.xloc + y * BOX_HTOTAL, y=self.yloc, fill=fill))


def AddYears(doc, year_start, year_end):
  for i in range(year_end - year_start):
    yr = year_start + i
    # + 1 is to make room for the start arrow.
    doc.AddChild(Text(y=VMARGIN + 10,
                      x=HMARGIN + BOX_HTOTAL * (i + 1) + BOX_WIDTH / 2, 
                      text=str(yr)))

def print_team(team, year_start, year_end, filter_players=True):
  d = Document()

  header = "%s: %i-%i" % (team.team_id, year_start, year_end)
  # Set up background.
  d.AddChild(Rect(x=0, y=0, width='100%', height='100%', fill='gray'))
  d.AddChild(Text(y=50, x=400, size=24, family='Verdana',
                  text=header, anchor='middle'))
  AddYears(d, int(year_start), int(year_end))

  if filter_players:
    team.players = [player for player in team.players if
                    len(player.years.keys()) > 4]

  for i, player in enumerate(team.players):
    d.AddChild(PlayerGroup(
        player, team,
        yloc=VMARGIN + BOX_VTOTAL * (i + 1),
        year_start=int(year_start), year_end=int(year_end)))
  print d

#parser = OptionParser()
#parser.add_option("-f", "--file", dest="in_filename",
#                  help="Read input from FILE", metavar="FILE")
#(options, args) = parser.parse_args()
#if __name__ == '__main__': main()
