class ButtonStyles:
    MODE_BUTTON = """
        QToolButton {
            background-color: #f0f0f0;
            border: 1px solid #999;
            border-radius: 5px;
            padding: 5px;
            min-width: 50px;
            min-height: 50px;
        }
        QToolButton:hover {
            background-color: #e0e0e0;
        }
        QToolButton:checked {
            background-color: #4CAF50;
            color: white;
            border: 2px solid #2E7D32;
        }
        QToolButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
    """
    
    DRAWING_BUTTON = """
        QToolButton {
            background-color: #f0f0f0;
            border: 1px solid #999;
            border-radius: 5px;
            padding: 5px;
            min-width: 50px;
            min-height: 50px;
        }
        QToolButton:hover {
            background-color: #e0e0e0;
        }
        QToolButton:checked {
            background-color: #2196F3;
            color: white;
            border: 2px solid #1976D2;
        }
        QToolButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
    """

    STATUS_LABEL = """
        QLabel {
            padding: 5px;
            border-radius: 3px;
            font-weight: bold;
        }
    """

    COORDS_LABEL = """
        QLabel {
            font-size: 14px;
            color: black;
            background-color: white;
            padding: 5px;
        }
    """ 