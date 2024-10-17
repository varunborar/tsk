import click
import os
import json

from Utils.Enums import SystemMode
from Utils.Values import available_categories
from Utils.InputHelper import single_select, file_select, text
from DataHandlers.Config import Config

class ConfigOptions():

    def __init__(self, edit, delete):
        self.edit = edit
        self.delete = delete

@click.group()
@click.option('-e', '--edit', is_flag=True, default=False, help='Edit the configuration')
@click.option('-d', '--delete', is_flag=True, default=False, help='Delete the configuration')
@click.pass_context
def config(context, edit, delete):
    '''
        Manage the configuration of application
    '''
    context.obj = ConfigOptions(edit, delete)

@config.command()
@click.argument('mode', type=click.Choice([e.value for e in SystemMode]), required=False)
@click.pass_obj
def mode(options, mode):
    '''
        View/Edit the system mode
    '''
    c = Config()
    if options.delete:
        print('Cannot delete the system mode')
    elif options.edit:
        if not mode:
            mode = single_select('System Mode', [e.value for e in SystemMode])
        c.set_mode(mode)
    else:
        print('System Mode:', c.get_mode())

@config.command()
@click.option('--data-dir', type=click.Path(exists=True), help='Data directory path')
@click.pass_obj
def file(options, data_dir):
    '''
        View/Edit the data directory
    '''
    c = Config()
    if options.delete:
        print('Cannot delete the data directory')
    elif options.edit:
        if not data_dir:
            data_dir = file_select('Data Directory')
            if data_dir.startswith('~'):
                data_dir = os.path.expanduser(data_dir)
        c.set_data_dir(data_dir)
    else:
        print('Data Directory:', c.get_data_dir())


@config.command()
@click.option('-c', '--category', type=click.Choice(available_categories()), help='Category name')
@click.argument('key', required=False)
@click.argument('value', required=False)
@click.pass_obj
def preference(options, category, key, value):
    '''
        View/Edit the preferences
    '''
    c = Config()
    if options.delete:
        if not category:
            category = c.get_default_category()
        if not key:
            c.clean_preferences()
        else:
            c.remove_preference(category, key)
    elif options.edit:
        if not category:
            category = c.get_default_category()
        if not key:
            key = text('Key')
        if not value:
            value = text('Value')
        c.set_preference(category, key, value)
    else:
        if not category:
            category = c.get_default_category()
        preference = c.get_preference(category, key)
        if not key:
            print(json.dumps(preference, indent=4))
        else:
            print(f'{category}.preferences.{key}: ', preference)

@config.command()
@click.option('-c', '--category', type=click.Choice(available_categories()), help='Category name')
@click.pass_obj
def default_category(options, category):
    '''
        View/Edit the default category
    '''
    c = Config()
    if options.delete:
        print('Cannot delete the default category')
    elif options.edit:
        if not category:
            category = single_select('Category', available_categories())
        c.set_default_category(category)
    else:
        print('Default Category:', c.get_default_category())



