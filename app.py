from textual.app import App, ComposeResult
from textual.widgets import Header, Button, Static, DataTable, Input, LoadingIndicator
from textual.containers import Container, Horizontal, VerticalScroll
from rich.text import Text
from css import CSS as styles
from database_conn import establish_connection, get_table_names, get_table_data, get_database_schema
from bedrock import Bedrock
import sys
import json


class DatabaseUI(App):

    TITLE = "Database Browser"
    CSS = styles

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("b", "back", "Back to Tables"),
        ("t", "toggle_mode", "Toggle Mode"),
        ("y", "confirm_commit", "Confirm Changes"),
        ("n", "cancel_commit", "Cancel Changes"),
    ]

    def __init__(self):
        super().__init__()
        self.view_state = "table_list"  # or "table_data"
        self.selected_table = None
        self.current_columns = []  # Store column names when viewing table data
        self.input_mode = "SQL"  # "AI" or "SQL"
        self.bedrock = None  # Will be initialized when switching to AI mode
        self.pending_commit = False  # Track if there's a pending commit

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Static("SQLITE Database UI", id="title")
        yield Horizontal(
            VerticalScroll(
                Static("Welcome to this service!", id="welcome-box"),
                id="welcome-scroll"
            ),
            VerticalScroll(
                DataTable(id="data-table"),
                id="table-scroll"
            ),
        )
        yield Horizontal(
            Static("📊 SQL Mode", id="mode-toggle"),
            LoadingIndicator(id="loading"),
            Static("", id="generated-sql"),
            id="mode-bar"
        )
        yield Input(placeholder="Enter SQL query...", id="text-input")

    def on_mount(self) -> None:
        """Called when app starts - set up the table"""
        table = self.query_one("#data-table", DataTable)
        table.cursor_type = "row"  # Enable row selection

        # Hide loading indicator initially
        self.query_one("#loading", LoadingIndicator).display = False

        # Disable focus on widgets we don't want in tab navigation
        self.query_one(Header).can_focus = False
        self.query_one("#title", Static).can_focus = False
        self.query_one("#welcome-scroll", VerticalScroll).can_focus = False
        self.query_one("#table-scroll", VerticalScroll).can_focus = False
        self.query_one("#welcome-box", Static).can_focus = False
        self.query_one("#mode-toggle", Static).can_focus = False
        self.query_one("#generated-sql", Static).can_focus = False
        self.query_one("#loading", LoadingIndicator).can_focus = False
        self.query_one("#mode-bar", Horizontal).can_focus = False

        # Set welcome instructions
        welcome = self.query_one("#welcome-box", Static)
        welcome.update(Text(
            "Database Browser\n\n"
            "How to use:\n"
            "• Click on a table to view its data\n"
            "• Click on a row to see details (JSON)\n"
            "• Click tab to switch widgets\n"
            "• Press 'b' to go back\n"
            "• Press 't' to switch modes\n"
            "• Press 'q' to quit\n"
            "• Ask anything in the text input\n"
            "  for AI assistance"
        ))

        self.db_conn = establish_connection(sys.argv[1])
        self.tables_names = get_table_names(self.db_conn)

        table.add_columns("Table Name", "Rows")

        for table_name, row_count in self.tables_names:
            table.add_row(table_name, str(row_count))


        self.query_one("#loading", LoadingIndicator).display = True
        self.run_worker(self._init_bedrock, exclusive=False, thread=True)

    def show_table_list(self) -> None:
        """Display the list of tables"""
        table = self.query_one("#data-table", DataTable)
        welcome = self.query_one("#welcome-box", Static)

        # Clear the table
        table.clear(columns=True)

        # Reset to table list view
        table.add_columns("Table Name", "Rows")
        for table_name, row_count in self.tables_names:
            table.add_row(table_name, str(row_count))

        # Update welcome box with instructions
        welcome.remove_class("left-align")
        welcome.update(Text(
            "Database Browser\n\n"
            "How to use:\n"
            "• Click on a table to view its data\n"
            "• Click on a row to see details (JSON)\n"
            "• Press tab to switch widgets\n"
            "• Press 'b' to go back\n"
            "• Press 't' to switch modes\n"
            "• Press 'q' to quit\n"
            "• Ask anything in the text input\n"
            "  for AI assistance"
        ))

        # Update state
        self.view_state = "table_list"

    def show_table_data(self, table_name: str) -> None:
        """Display data from selected table"""
        table = self.query_one("#data-table", DataTable)
        welcome = self.query_one("#welcome-box", Static)

        # Get table data
        columns, rows = get_table_data(self.db_conn, table_name)

        # Store columns for row selection
        self.current_columns = columns

        # Clear the table
        table.clear(columns=True)

        # Add columns from the selected table
        table.add_columns(*columns)

        # Add rows
        for row in rows:
            # Convert row to strings for display
            table.add_row(*[str(val) for val in row])

        # Update welcome box with viewing message
        welcome.remove_class("left-align")
        welcome.update(Text(f"Viewing: {table_name}\n\nPress 'b' to go back"))

        # Update state
        self.view_state = "table_data"
        self.selected_table = table_name

    def show_row_details(self, event: DataTable.RowSelected) -> None:
        """Display selected row as formatted JSON in welcome box"""
        table = event.data_table
        row_index = event.cursor_row

        row = table.get_row_at(row_index)

        row_dict = {}
        for i, col_name in enumerate(self.current_columns):
            row_dict[col_name] = row[i]

        # Format as pretty JSON
        json_str = json.dumps(row_dict, indent=2, default=str)

        # Update welcome box with JSON
        welcome = self.query_one("#welcome-box", Static)
        welcome.add_class("left-align")
        welcome.update(Text(f"Row Details:\n\n{json_str}"))

    def action_back(self) -> None:
        """Handle back action (b key)"""
        if self.view_state == "table_data":
            self.show_table_list()

    def action_confirm_commit(self) -> None:
        """Confirm and commit pending changes (y key)"""
        if self.pending_commit:
            self.db_conn.commit()
            self.pending_commit = False
            self.notify("✓ Changes committed successfully", severity="information")
            # Refocus input for next query
            self.query_one("#text-input", Input).focus()

    def action_cancel_commit(self) -> None:
        """Cancel and rollback pending changes (n key)"""
        if self.pending_commit:
            self.db_conn.rollback()
            self.pending_commit = False
            self.notify("✗ Changes rolled back", severity="warning")
            # Refocus input for next query
            self.query_one("#text-input", Input).focus()

    def _init_bedrock(self) -> None:
        """Initialize Bedrock client in background"""
        try:
            self.bedrock = Bedrock()
            # Run health check to verify it's working
            self.bedrock.check_health()
            self.query_one("#loading", LoadingIndicator).display = False
            self.notify("AI assistant ready!", severity="information")
        except Exception as e:
            self.bedrock = None
            self.query_one("#loading", LoadingIndicator).display = False
            self.notify(f"Failed to initialize AI: {str(e)}", severity="error")

            # Show error in welcome box
            welcome = self.query_one("#welcome-box", Static)
            welcome.add_class("left-align")
            welcome.update(Text(f"AI Initialization Failed\n\n{str(e)}\n\nPlease check your AWS credentials and configuration."))

    def action_toggle_mode(self) -> None:
        """Toggle between AI and SQL mode"""
        toggle = self.query_one("#mode-toggle", Static)
        input_field = self.query_one("#text-input", Input)

        if self.input_mode == "AI":
            self.input_mode = "SQL"
            toggle.update("📊 SQL Mode")
            input_field.placeholder = "Enter SQL query..."
            # Clear generated SQL when switching to SQL mode
            self.query_one("#generated-sql", Static).update("")
        else:
            self.input_mode = "AI"
            toggle.update("⚡ AI Mode")
            input_field.placeholder = "Ask anything for AI assistance..."


    def display_sql_results(self, columns, rows, query):
        """Display SQL query results in the welcome box"""
        welcome = self.query_one("#welcome-box", Static)

        # Format the output
        result_text = f"SQL Query:\n{query}\n\n"
        result_text += f"Returned {len(rows)} row(s)\n\n"

        if rows:
            # Special handling for schema queries (sqlite_master)
            if 'sql' in columns and len(columns) <= 2:
                # Display CREATE statements directly without JSON encoding
                for row in rows:
                    for i, col in enumerate(columns):
                        if row[i]:  # Skip None values
                            if col == 'sql':
                                result_text += f"{row[i]}\n\n"
                            else:
                                result_text += f"{col}: {row[i]}\n"
            else:
                # Format as JSON list for normal queries
                result_list = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        row_dict[col] = row[i]
                    result_list.append(row_dict)

                result_text += json.dumps(result_list, indent=2, default=str)
        else:
            result_text += "No results"

        welcome.add_class("left-align")
        welcome.update(Text(result_text))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the DataTable"""
        if self.view_state == "table_list":
            # Viewing table list: select a table to view its data
            table = event.data_table
            row_index = event.cursor_row
            row = table.get_row_at(row_index)
            table_name = row[0]  # First column is the table name
            self.show_table_data(table_name)

        elif self.view_state == "table_data":
            # Viewing table data: show selected row details as JSON
            self.show_row_details(event)

    def execute_sql_query(self, sql_query: str, original_text: str = None, auto_commit: bool = True) -> int:
        """Execute SQL query and display results. Returns rowcount for modification queries."""
        try:
            cursor = self.db_conn.execute(sql_query)

            # Check if it's a SELECT query (has description) or modification query (no description)
            if cursor.description:
                # SELECT query - show results
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                self.display_sql_results(columns, rows, original_text or sql_query)
                self.notify(f"Query returned {len(rows)} rows", severity="information")
                return 0
            else:
                # UPDATE/DELETE/INSERT query - show affected rows
                rowcount = cursor.rowcount

                if auto_commit:
                    welcome = self.query_one("#welcome-box", Static)
                    welcome.add_class("left-align")
                    welcome.update(Text(f"SQL Query:\n{sql_query}\n\n✓ Query executed successfully\n{rowcount} row(s) affected"))
                    self.db_conn.commit()
                    self.notify(f"Query executed: {rowcount} row(s) affected", severity="information")

                return rowcount

        except Exception as e:
            # Show error in left box
            welcome = self.query_one("#welcome-box", Static)
            welcome.add_class("left-align")
            welcome.update(Text(f"SQL Error:\n\n{str(e)}"))
            self.notify(f"SQL Error: {str(e)}", severity="error")
            return 0

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle text input submission"""
        text = event.value
        if text.strip():
            # Clear input
            event.input.value = ""

            # Show loading indicator
            self.query_one("#loading", LoadingIndicator).display = True

            try:
                if self.input_mode == "AI":
                    # Check if Bedrock is initialized
                    if not self.bedrock:
                        self.query_one("#loading", LoadingIndicator).display = False
                        welcome = self.query_one("#welcome-box", Static)
                        welcome.add_class("left-align")
                        welcome.update(Text("AI assistant not initialized.\n\nPlease check your AWS credentials and try toggling AI mode again (press 't' twice)."))
                        self.notify("AI assistant not available", severity="error")
                        return

                    # Get SQL from AI
                    schema = get_database_schema(self.db_conn)
                    sql_query = self.bedrock.get_sql(text, schema)

                    # Check if AI determined no query is needed
                    if sql_query == "NO_QUERY_NEEDED":
                        self.query_one("#generated-sql", Static).update("")
                        welcome = self.query_one("#welcome-box", Static)
                        welcome.add_class("left-align")
                        welcome.update(Text(f"Request: {text}\n\nUnable to interpret a database query from this request.\nPlease provide more specific information or ask questions about your data."))
                        self.notify("Could not interpret query from request", severity="information")
                    else:
                        # Display the generated SQL
                        self.query_one("#generated-sql", Static).update(f"SQL: {sql_query}")

                        # Check if it's a data-modifying query
                        sql_upper = sql_query.strip().upper()
                        is_modifying = sql_upper.startswith(('INSERT', 'UPDATE', 'DELETE'))

                        if is_modifying:
                            # Execute without committing and ask for confirmation
                            affected_rows = self.execute_sql_query(sql_query, original_text=text, auto_commit=False)
                            self.pending_commit = True

                            # Blur input so y/n keys work for confirmation
                            self.query_one("#text-input", Input).blur()

                            # Show confirmation message
                            welcome = self.query_one("#welcome-box", Static)
                            welcome.update(Text(f"SQL Query:\n{sql_query}\n\n⚠️ PENDING: {affected_rows} row(s) will be affected\n\nCONFIRM CHANGES?\nPress 'y' to commit or 'n' to cancel"))
                            self.notify(f"Press 'y' to commit or 'n' to cancel ({affected_rows} rows)", severity="warning")
                        else:
                            # SELECT query - execute normally
                            self.execute_sql_query(sql_query, original_text=text)
                else:
                    # Execute SQL directly
                    # Clear generated SQL display when in SQL mode
                    self.query_one("#generated-sql", Static).update("")
                    self.execute_sql_query(text)
            except Exception as e:
                welcome = self.query_one("#welcome-box", Static)
                welcome.add_class("left-align")
                welcome.update(Text(f"Error:\n\n{str(e)}"))
                self.notify(f"Error: {str(e)}", severity="error")
            finally:
                # Hide loading indicator when done
                self.query_one("#loading", LoadingIndicator).display = False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run app.py <database.db>")
        sys.exit(1)

    app = DatabaseUI()
    app.run()

