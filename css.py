CSS = """
    Screen {
        background: #1e1e2e;
    }

    Header {
        background: #1e1e2e;
        color: #f5e0dc;
        border-bottom: thick #89b4fa;
    }

    Container {
        align: center middle;
        background: #1e1e2e;
    }

    #title {
        text-align: center;
        text-style: bold;
        background: #1e1e2e;
        color: #89dceb;
        padding: 1 2;
        margin: 0;
        border-bottom: thick #89b4fa;
    }

    Horizontal {
        height: 1fr;
        margin: 0;
    }

    #welcome-scroll {
        width: 50%;
        height: 100%;
        margin: 1;
        border-left: heavy #89b4fa;
        border-right: solid #45475a;
        border-top: solid #45475a;
        border-bottom: solid #45475a;
    }

    #welcome-box {
        width: 100%;
        height: auto;
        padding: 3 2;
        margin: 0;
        background: #1e1e2e;
        color: #f5e0dc;
        text-align: left;
    }

    #welcome-box.left-align {
        text-align: left;
    }

    Button {
        margin: 1;
        background: #313244;
        color: #cdd6f4;
        border: solid #45475a;
    }

    Button:hover {
        background: #45475a;
        color: #f5e0dc;
    }

    Button:focus {
        border: solid #89b4fa;
    }

    Button#add-btn {
        background: #1e3a2e;
        border: solid #40a478;
    }

    Button#add-btn:hover {
        background: #2d5a45;
        color: #a6e3a1;
    }

    Button#exit-btn {
        background: #3e2a2a;
        border: solid #a14040;
    }

    Button#exit-btn:hover {
        background: #5a3535;
        color: #f38ba8;
    }

    #table-scroll {
        width: 50%;
        height: 100%;
        margin: 1;
        border-left: heavy #89b4fa;
        border-right: solid #45475a;
        border-top: solid #45475a;
        border-bottom: solid #45475a;
    }

    DataTable {
        width: 100%;
        height: auto;
        margin: 0;
        background: #1e1e2e;
    }

    DataTable > .datatable--header {
        background: #181825;
        color: #f5e0dc;
        text-style: bold;
    }

    DataTable > .datatable--cursor {
        background: #313244;
        color: #f5e0dc;
    }

    DataTable:focus > .datatable--cursor {
        background: #45475a;
        color: #f5e0dc;
    }

    DataTable > .datatable--odd-row {
        background: #181825;
    }

    DataTable > .datatable--even-row {
        background: #1e1e2e;
    }

    #mode-bar {
        height: auto;
        margin: 0;
        padding: 0;
        align: left middle;
    }

    #mode-toggle {
        width: auto;
        height: auto;
        padding: 0 1;
        margin: 0 0 0 1;
        background: transparent;
        border: none;
        color: #89b4fa;
        text-align: left;
    }

    #loading {
        width: auto;
        height: auto;
        margin: 0 1;
        color: #89b4fa;
    }

    #generated-sql {
        width: auto;
        height: auto;
        margin: 0 1;
        color: #cdd6f4;
        text-style: italic;
    }

    Input {
        margin: 1;
        padding: 0 1;
        background: #1e1e2e;
        border-top: heavy #89b4fa;
        border-left: solid #45475a;
        border-right: solid #45475a;
        border-bottom: solid #45475a;
        color: #f5e0dc;
    }

    Input:focus {
        border-top: heavy #89b4fa;
    }

    Input > .input--placeholder {
        color: #6c7086;
        text-style: italic;
    }

    Toast {
        offset: -1 -1;
    }
    """
