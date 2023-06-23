class TableSAP:
    def __init__(self, table) -> None:
        self.table = table
        # Set the table headers
        self.table.setColumnCount(7)  # Set three columns
        self.table.setHorizontalHeaderLabels(
            ["Положение X", "Положение  Y", "Вынос X", "Вынос Y", "Интенсивность", "Размер X", "Размер Y"])
        self.table.resizeColumnsToContents()

        self.Chkp_list: list = []

    def add_element(self) -> None:
        # визуальное отражение
        rowPosition = self.table.rowCount()
        self.table.insertRow(rowPosition)
        # print(self.table.rowCount())
        # логическое отражение

    def delete_elevent(self) -> None:
        if self.table.currentRow() >= 0:
            row = self.table.currentRow()
            print(row)
            self.table.removeRow(row)
