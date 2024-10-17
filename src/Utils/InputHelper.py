from InquirerPy import inquirer, get_style # type: ignore
from yaspin import yaspin # type: ignore
from yaspin.constants import SPINNER_ATTRS # type: ignore
from yaspin.spinners import Spinners # type: ignore
from types import SimpleNamespace
from functools import wraps
import os

default_config = {
    "qmark": "?",
    "amark": "*",
    "pointer": ">",
    "height": None,
    "max_height": None,
    "border": True,
    "marker": "@",
    "marker_pl": " ",
    "enabled_symbol": "◉",
    "disabled_symbol": "◯",
    "prompt": "?",
    "vi_mode": False,
    "show_cursor": True,
    "cycle": True,
    "wrap_lines": True,
    "raise_keyboard_interrupt": True,
    "multicolumn_complete": False,
    "decimal_symbol": ".",
    "replace_mode": True,
    "info": True,
    "exact_symbol": " E",
}

default_spinner_attributes = {
    'success_symbol': '✔',
    'fail_symbol': '✘',
    'spinner': 'bouncingBar',
    'spinner_color': 'yellow',
    'show_success': False
}

default_messages = {
    "mandatory": "This is a required field",
    "invalid": "Invalid input",
}

default_keybindings = {
    "single_select": {
        "answer": [{"key": "enter"}],
        "interrupt": [{"key": "c-c"}],
        "skip": [{"key": "s-down"}],
    },
    "multi_select": {
        "answer": [{"key": "enter"}],
        "interrupt": [{"key": "c-c"}],
        "skip": [{"key": "s-down"}],
    },
    "text": {
        "answer": [{"key": "enter"}],
        "interrupt": [{"key": "c-c"}],
        "skip": [{"key": "s-right"}],
    },
    "number": {
        "answer": [{"key": "enter"}],
        "interrupt": [{"key": "c-c"}],
        "skip": [{"key": "s-down"}],
    },
    "fuzzy": {
        "answer": [{"key": "enter"}],
        "interrupt": [{"key": "c-c"}],
        "skip": [{"key": "s-down"}],
    }
}

default_style = get_style({
    "questionmark": "#e5c07b",
    "answermark": "#e5c07b",
    "answer": "#61afef",
    "input": "#98c379",
    "question": "",
    "answered_question": "",
    "instruction": "#abb2bf",
    "long_instruction": "#abb2bf",
    "pointer": "#61afef",
    "checkbox": "#98c379",
    "separator": "yellow",
    "skipped": "#5c6370",
    "validator": "",
    "marker": "#e5c07b",
    "fuzzy_prompt": "#c678dd",
    "fuzzy_info": "#abb2bf",
    "fuzzy_border": "#4b5263",
    "fuzzy_match": "#c678dd",
    "spinner_pattern": "#e5c07b",
    "spinner_text": ""
})

default_config = SimpleNamespace(**default_config)
default_keybindings = SimpleNamespace(**default_keybindings)
default_messages = SimpleNamespace(**default_messages)
default_spinner_attributes = SimpleNamespace(**default_spinner_attributes)

validate_non_empty = lambda x: True if x else False

"""
    Utility Functions
"""

def get_defaults(kwargs):
    config = kwargs.get('config', default_config)
    style = kwargs.get('style', default_style)
    keybindings = kwargs.get('keybindings', default_keybindings)
    return config, style, keybindings

def _merge_dicts(dict1, dict2):
    merged_dict = dict1.copy()

    for key, value in dict2.items():
        if key in merged_dict:
            if isinstance(merged_dict[key], dict) and isinstance(value, dict):
                merged_dict[key] = _merge_dicts(merged_dict[key], value)
            else:
                merged_dict[key] = value
        else:
            merged_dict[key] = value
    return merged_dict

def get_completer_from_suggestions(suggestions: list, separator=None) -> dict:
    completer = None

    def _get_completer(suggestion):
        if isinstance(suggestion, str):
            return {suggestion: None}
        elif isinstance(suggestion, list):
            if len(suggestion) == 1:
                return {suggestion[0]: None}
            return {
                suggestion[0]: _get_completer(suggestion[1:])
            }

    if suggestions:
        if separator:
            suggestions = [ suggestion.split(separator) for suggestion in suggestions ]
        completer = {}
        for suggestion in suggestions:
            _completer = _get_completer(suggestion)
            completer = _merge_dicts(completer, _completer)
    return completer

def spin_while_execute(func, message, *args, **kwargs):

    spinner_attributes = {key: value for key, value in kwargs.items() if key.startswith('_')}
    for key in spinner_attributes:
        del kwargs[key]

    spinner = getattr(Spinners, spinner_attributes.get('_spinner', default_spinner_attributes.spinner))
    with yaspin(spinner, text=message, color=spinner_attributes.get('_spinner_color', default_spinner_attributes.spinner_color)) as spinner:
        result = func(*args, **kwargs)
        if spinner_attributes.get('_show_success', default_spinner_attributes.show_success):
            spinner.ok(spinner_attributes.get('_success_symbol', default_spinner_attributes.success_symbol))
        return result

def load(message, **spin_options):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            spinner = getattr(Spinners, spin_options.get('_spinner', default_spinner_attributes.spinner))  # Default spinner
            color = spin_options.get('_spinner_color', default_spinner_attributes.spinner_color)  # Default color
            show_success = spin_options.get('_show_success', default_spinner_attributes.show_success)  # Show success by default
            success_symbol = spin_options.get('_success_symbol', default_spinner_attributes.success_symbol)  # Default success symbol
            fail_symbol = spin_options.get('_fail_symbol', default_spinner_attributes.fail_symbol)  # Default fail symbol

            # Using yaspin spinner
            with yaspin(spinner, text=message, color=color) as spinner:
                try:
                    # Execute the original function
                    result = func(*args, **kwargs)
                    if show_success:
                        spinner.ok(success_symbol)  # Success symbol on completion
                    return result
                except Exception as e:
                    spinner.fail(fail_symbol)  # Failure symbol on exception
                    raise e  # Re-raise the exception

        return wrapper

    return decorator

"""
    Input Helper functions
"""

def single_select(
        message,
        choices,
        default=None,
        instruction='',
        long_instruction='',
        transformer=None,
        filter=None,
        validate=None,
        invalid_message=default_messages.invalid,
        mandatory=True,
        mandatory_message=default_messages.mandatory,
       **kwargs
    ):
    """Prompt user to select one option from a list of choices."""

    config, style, keybindings = get_defaults(kwargs)

    prompt = inquirer.select(
        message=message + (' (*)' if mandatory else ''),
        choices=choices,
        default=default,
        style=style,
        vi_mode=config.vi_mode,
        qmark=config.qmark,
        amark=config.amark,
        pointer=config.pointer,
        instruction=instruction,
        long_instruction=long_instruction,
        transformer=transformer,
        filter=filter,
        height=config.height,
        max_height=config.max_height,
        multiselect=False,
        marker=config.marker,
        marker_pl=config.marker_pl,
        border=config.border,
        validate=validate,
        invalid_message=invalid_message,
        keybindings=keybindings.single_select,
        show_cursor=config.show_cursor,
        cycle=config.cycle,
        wrap_lines=config.wrap_lines,
        raise_keyboard_interrupt=config.raise_keyboard_interrupt,
        mandatory=mandatory,
        mandatory_message=mandatory_message
    )

    if 'return_prompt' in kwargs and kwargs['return_prompt']:
        return prompt
    return prompt.execute()

def multi_select(
        message,
        choices,
        default=None,
        instruction='',
        long_instruction='',
        transformer=None,
        filter=None,
        validate=None,
        invalid_message=default_messages.invalid,
        mandatory=True,
        mandatory_message=default_messages.mandatory,
       **kwargs
    ):
    """Prompt user to select multiple options from a list of choices."""

    config, style, keybindings = get_defaults(kwargs)

    prompt = inquirer.select(
        message=message + (' (*)' if mandatory else ''),
        choices=choices,
        default=default,
        style=style,
        vi_mode=config.vi_mode,
        qmark=config.qmark,
        amark=config.amark,
        pointer=config.pointer,
        instruction=instruction,
        long_instruction=long_instruction,
        transformer=transformer,
        filter=filter,
        height=config.height,
        max_height=config.max_height,
        multiselect=True,
        marker=config.marker,
        marker_pl=config.marker_pl,
        border=config.border,
        validate=validate,
        invalid_message=invalid_message,
        keybindings=keybindings.single_select,
        show_cursor=config.show_cursor,
        cycle=config.cycle,
        wrap_lines=config.wrap_lines,
        raise_keyboard_interrupt=config.raise_keyboard_interrupt,
        mandatory=mandatory,
        mandatory_message=mandatory_message
    )

    if 'return_prompt' in kwargs and kwargs['return_prompt']:
        return prompt
    return prompt.execute()

def text(
        message,
        default='',
        instruction='',
        long_instruction='',
        suggestions=None,
        multiline=False,
        validate=None,
        invalid_message=default_messages.invalid,
        transformer=None,
        filter=None,
        mandatory=True,
        mandatory_message=default_messages.mandatory,
        **kwargs
    ):
    """Prompt user to input text."""
    config, style, keybindings = get_defaults(kwargs)

    prompt = inquirer.text(
        message=message + (' (*)' if mandatory else ''),
        style=style,
        vi_mode=config.vi_mode,
        default=default,
        qmark=config.qmark,
        amark=config.amark,
        instruction=instruction,
        long_instruction=long_instruction,
        completer=get_completer_from_suggestions(suggestions, separator=kwargs.get('suggestion_separator', None)) if isinstance(suggestions, list) else suggestions,
        multicolumn_complete=config.multicolumn_complete,
        multiline=multiline,
        validate=validate,
        invalid_message=invalid_message,
        transformer=transformer,
        filter=filter,
        keybindings=keybindings.text,
        wrap_lines=config.wrap_lines,
        raise_keyboard_interrupt=config.raise_keyboard_interrupt,
        is_password=False,
        mandatory=mandatory,
        mandatory_message=mandatory_message
    )

    if 'return_prompt' in kwargs and kwargs['return_prompt']:
        return prompt
    result = prompt.execute()

    if kwargs.get('return_transformed_result', False):
        return transformer(result) if transformer else result
    return result

def number(
        message,
        default=0,
        float_allowed=False,
        max_allowed=None,
        min_allowed=None,
        instruction='',
        validate=None,
        invalid_message=default_messages.invalid,
        transformer=None,
        filter=None,
        mandatory=True,
        mandatory_message=default_messages.mandatory,
        **kwargs
    ):
    """Prompt user to input a number."""
    config, style, keybindings = get_defaults(kwargs)

    prompt = inquirer.number(
        message=message + (' (*)' if mandatory else ''),
        style=style,
        vi_mode=config.vi_mode,
        default=default,
        qmark=config.qmark,
        amark=config.amark,
        float_allowed=float_allowed,
        max_allowed=max_allowed,
        min_allowed=min_allowed,
        decimal_symbol=config.decimal_symbol,
        replace_mode=config.replace_mode,
        instruction="",
        long_instruction=instruction,
        validate=validate,
        invalid_message=invalid_message,
        transformer=transformer,
        filter=filter,
        keybindings=keybindings.number,
        wrap_lines=config.wrap_lines,
        raise_keyboard_interrupt=config.raise_keyboard_interrupt,
        mandatory=mandatory,
        mandatory_message=mandatory_message
    )

    if 'return_prompt' in kwargs and kwargs['return_prompt']:
        return prompt
    return prompt.execute()


def fuzzy_select(
    message,
    choices,
    default='',
    transformer=None,
    filter=None,
    instruction='',
    long_instruction='',
    match_exact=False,
    validate=None,
    invalid_message=default_messages.invalid,
    mandatory=True,
    mandatory_message=default_messages.mandatory,
    **kwargs
    ):
    """Prompt user to select one option from a list of choices."""
    config, style, keybindings = get_defaults(kwargs)
    prompt = inquirer.fuzzy(
        message,
        choices,
        default=default,
        pointer=config.pointer,
        style=style,
        vi_mode=config.vi_mode,
        qmark=config.qmark,
        amark=config.amark,
        transformer=transformer,
        filter=filter,
        instruction=instruction,
        long_instruction=long_instruction,
        multiselect=False,
        prompt=config.prompt,
        marker=config.marker,
        marker_pl=config.marker_pl,
        border=config.border,
        info=config.info,
        match_exact=match_exact,
        exact_symbol=config.exact_symbol,
        height=config.height,
        max_height=config.max_height,
        validate=validate,
        invalid_message=invalid_message,
        keybindings=keybindings.fuzzy,
        cycle=config.cycle,
        wrap_lines=config.wrap_lines,
        raise_keyboard_interrupt=config.raise_keyboard_interrupt,
        mandatory=mandatory,
        mandatory_message=mandatory_message
    )

    if 'return_prompt' in kwargs and kwargs['return_prompt']:
        return prompt
    return prompt.execute()

def fuzzy_multi_select(
    message,
    choices,
    default='',
    transformer=None,
    filter=None,
    instruction='',
    long_instruction='',
    match_exact=False,
    validate=None,
    invalid_message=default_messages.invalid,
    mandatory=True,
    mandatory_message=default_messages.mandatory,
    **kwargs
    ):
    """Prompt user to select multiple option from a list of choices."""
    config, style, keybindings = get_defaults(kwargs)
    prompt = inquirer.fuzzy(
        message,
        choices,
        default=default,
        pointer=config.pointer,
        style=style,
        vi_mode=config.vi_mode,
        qmark=config.qmark,
        amark=config.amark,
        transformer=transformer,
        filter=filter,
        instruction=instruction,
        long_instruction=long_instruction,
        multiselect=True,
        prompt=config.prompt,
        marker=config.marker,
        marker_pl=config.marker_pl,
        border=config.border,
        info=config.info,
        match_exact=match_exact,
        exact_symbol=config.exact_symbol,
        height=config.height,
        max_height=config.max_height,
        validate=validate,
        invalid_message=invalid_message,
        keybindings=keybindings.fuzzy,
        cycle=config.cycle,
        wrap_lines=config.wrap_lines,
        raise_keyboard_interrupt=config.raise_keyboard_interrupt,
        mandatory=mandatory,
        mandatory_message=mandatory_message
    )

    if 'return_prompt' in kwargs and kwargs['return_prompt']:
        return prompt
    return prompt.execute()

def file_select(
    message,
    default=None,
    instruction='',
    long_instruction='',
    validate=None,
    invalid_message=default_messages.invalid,
    mandatory=True,
    mandatory_message=default_messages.mandatory,
    **kwargs
    ):    
    """Prompt user to select a file."""
    config, style, keybindings = get_defaults(kwargs)

    if not default:
        default = "~/" if os.name == "posix" else "C:\\"

    prompt = inquirer.filepath(
        message=message + (' (*)' if mandatory else ''),
        style=style,
        vi_mode=config.vi_mode,
        default=default,
        qmark=config.qmark,
        amark=config.amark,
        instruction=instruction,
        long_instruction=long_instruction,
        validate=validate,
        invalid_message=invalid_message,
        keybindings=keybindings.text,
        wrap_lines=config.wrap_lines,
        raise_keyboard_interrupt=config.raise_keyboard_interrupt,
        mandatory=mandatory,
        mandatory_message=mandatory_message
    )

    if 'return_prompt' in kwargs and kwargs['return_prompt']:
        return prompt
    
    return prompt.execute()