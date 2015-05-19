#!/usr/bin/env python3
# coding: utf-8

import cat

q = cat.Question('What can I do for you ?\n> ')


@q.script('Bring me some {thing:(\w|\s)+}, please{:\.?}')
def bring_me_some(match):
    print("I'll bring you some {} for sure.".format(match.group('thing')))

q.ask()
