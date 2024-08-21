""" Dimension classification """

from typing import List, Tuple
import pandas

DATETIME_REGEX_PATTERNS = {
    "%d/%m/%Y": '|'.join([
        r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d\d\d\d$',
        r'^([1-9]|[12][0-9]|3[01])/([1-9]|1[0-2])/\d\d\d\d$'
    ]),
    "%m/%d/%Y": '|'.join([
        r'^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/\d\d\d\d$',
        r'^([1-9]|1[0-2])/([1-9]|[12][0-9]|3[01])/\d\d\d\d$'
    ]),
    "%Y-%m-%d": '|'.join([
        r'^\d\d\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
        r'^\d\d\d\d-([1-9]|1[0-2])-([1-9]|[12][0-9]|3[01])$'
    ]),
    "%Y/%m/%d": '|'.join([
        r'^\d\d\d\d/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])$'
        r'^\d\d\d\d/([1-9]|1[0-2])/([1-9]|[12][0-9]|3[01])$'
    ]),
    "%d %b %Y": '|'.join([
        ' '.join([
            r'^(0[1-9]|[12][0-9]|3[01])',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
            r'\d\d\d\d$',
        ]),
        ' '.join([
            r'^([1-9]|[12][0-9]|3[01])',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
            r'\d\d\d\d$'
        ])
    ]),
    "%d%b%Y": '|'.join([
        ''.join([
            r'^(0[1-9]|[12][0-9]|3[01])',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
            r'\d\d\d\d$'
        ]),
        ''.join([
            r'^([1-9]|[12][0-9]|3[01])',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
            r'\d\d\d\d$'
        ])
    ]),
    "%b %d, %Y": '|'.join([
        ' '.join([
            r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
            r'(0[1-9]|[12][0-9]|3[01]),',
            r'\d\d\d\d$'
        ]),
        ' '.join([
            r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
            r'([1-9]|[12][0-9]|3[01]),',
            r'\d\d\d\d$'
        ])
    ])
}


def datetime_dimension(
    df: pandas.DataFrame
) -> List[Tuple[str, str]]:
    """ Parses `df` and returns a list of date-time columns and formats as a `List[Tuple[str, str]]`.

    Parameters
    ----------
    df : `pandas.DataFrame`
        Pandas dataframe object to describe.
    """

    date_dimensions = []

    # Retain column and datatype
    for col in df.columns:
        for pattern in DATETIME_REGEX_PATTERNS.values():
            if all(df[col].astype(str).str.match(pattern, na=False)):
                date_dimensions.append(
                    (
                        col,
                        list(DATETIME_REGEX_PATTERNS.keys())[
                            list(DATETIME_REGEX_PATTERNS.values()).index(pattern)
                        ]
                    )
                )
                break

    return date_dimensions
