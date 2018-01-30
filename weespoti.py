#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus
import re
import weechat

name    = "weespotipy"
author  = "Lorenz Wellmer"
version = "1.0"
desc    = "Weechat Spotify"
license = "GPL3"
command = "wspy"

class DBusClient(object):
   def __init__(self, bus=None):
      self.obj_path = "/org/mpris/MediaPlayer2"
      self.prop_path = "org.freedesktop.DBus.Properties"
      self.player_path = "org.mpris.MediaPlayer2.Player"
      self.spotify_path = None

      self.connect_to_spotify_dbus(bus)


   def connect_to_spotify_dbus(self, bus):
      if not bus:
         bus = dbus.SessionBus()
      self.session_bus = bus

      for name in bus.list_names():
         if re.match(r".*mpris.*spotify", name):
            self.spotify_path = str(name)

      try:
         self.proxy = self.session_bus.get_object(self.spotify_path, self.obj_path)
         self.properties = dbus.Interface(self.proxy, self.prop_path)
         self.player = dbus.Interface(self.proxy, self.player_path)
      except Exception:
         weechat.prnt("", "%Could not connect to Spotify dbus session!" % weechat.prefix("error"))


   def get_property(self, key):
      prop = None
      
      try:
         prop = self.properties.Get(self.player_path, key)
      except dbus.exceptions.DBusException as e:
         self.connect_to_spotify_dbus(None)
         weechat.prnt("", "%failed to get DBus property" % weechat.prefix("error"))
      
      return prop


   def get_song(self):
      title = ""
      artist = ""

      try:
         metadata = self.get_property("Metadata")
         title = str(metadata["xesam:title"])
         artist = str(metadata["xesam:artist"][0])
      except Exception as e:
         weechat.prnt("", "%Cannot get song info" % weechat.prefix("error"))

      return artist, title


def ws_command(data, buffer, args):
   try:
      song = dbc.get_song()
      artist, title = dbc.get_song()
      string = u"%s♫ %sNow playing:%s %s%s - %s%s %s♫" % ("\x034", "\x0312", "\x038", artist, "\x0312", "\x039", title, "\x034")
      weechat.command(buffer, string.encode("UTF-8"))
   except Exception as err:
      weechat.prnt("", "%sException: %s" % (weechat.prefix("error"), err))
   finally:
      return weechat.WEECHAT_RC_OK


def main():
   global dbc
   dbc = DBusClient()
   weechat.register(name, author, version, license, desc, "", "") 
   weechat.hook_command(command, desc, "", "", "", "ws_command", "")
   weechat.prnt("", "%s | %s" % (name, author))


if __name__ == "__main__":
   main()
