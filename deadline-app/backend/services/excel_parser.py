import openpyxl
import re
from rapidfuzz import fuzz
from dateutil.parser import parse as parse_date
from dateutil.parser import ParserError
from datetime import date, datetime

class ExcelParser:
    TAB1_HEADER_ROW = 6 # data starts at row 6 in Tab 1
    TAB2_HEADER_ROW = 9 # data starts at row 9 in Tab 2

    def __init__(self, file):
        self.wb = openpyxl.load_workbook(file)

    def detect_tabs(self) -> dict:
        return {
            "sheet_names": self.wb.sheetnames,
            "suggested": {
                "tab1": self._suggest_tab("documents tracking theo doi cv"),
                "tab2": self._suggest_tab("directives meeting chi dao ldp")
            }
        }

    def _suggest_tab(self, keywords: str) -> str:
        def score(name):
            return fuzz.partial_ratio(keywords, name.lower())
        return max(self.wb.sheetnames, key=score)
    
    def extract_staff_names(self, text: str) -> list:
        if not text:
            return []
        names = re.split(r'[\n,;]+', str(text))
        return [name.strip() for name in names if name.strip() and len(name.strip()) <= 100]

    def detect_recurring(self, text: str) -> tuple:
        if not text:
            return (False, None)

        recurring_keywords = {
            "mỗi ngày", "hàng ngày", "hàng tuần",
            "hàng tháng", "thường xuyên", "daily", "weekly", "monthly", "yearly", "annually",
            "recurring", "recurrent", "ongoing", "regular", "regularly",
            "every day", "every week", "every month", "continuous"
        } 
        text_lower = str(text).lower()

        for keyword in recurring_keywords:
            if keyword in text_lower:
                return (True, str(text).strip())

        return (False, None)
    
    def extract_deadline(self, text: str):
        if not text:
            return None
        
        # if already a date or datetime obj - return directly
        if isinstance(text, datetime):
            return text.date()
        if isinstance(text, date):
            return text

        text = str(text)

        iso_matches = re.findall(r'\d{4}-\d{2}-\d{2}', text)
        if iso_matches:
            try:
                return parse_date(iso_matches[-1]).date()
            except ParserError:
                pass

        slash_matches = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', text)
        if slash_matches:
            try:
                return parse_date(slash_matches[-1], dayfirst=True).date()
            except ParserError:
                pass

        return None
    
    def _parse_date(self, value) -> date:
        if value is None:
            return None
        
        # already a date
        if hasattr(value, 'date'):
            return value.date()
        if isinstance(value, date):
            return value
        #string date - parse it
        try:
            return parse_date(str(value), dayfirst=True).date()
        except (ParserError, ValueError):
            return None

    def parse_tab1(self, sheet, header_row: int = None) -> tuple:
        header_row = header_row or self.TAB1_HEADER_ROW
        documents = []
        flagged = []

        #skip header rows, start at row 4
        for row in sheet.iter_rows(min_row=header_row, values_only=True):
            if not any(row):
                continue

            row_number    = int(row[0]) if row[0] else None
            received_date = self._parse_date(row[1])
            doc_type      = str(row[2]).strip() if row[2] is not None else None
            content       = str(row[3]).strip() if row[3] is not None else None
            reference     = str(row[4]).strip() if row[4] is not None else None
            requirement   = str(row[5]).strip() if row[5] is not None else None
            staff_text    = str(row[6]).strip() if row[6] is not None else None
            result        = str(row[7]).strip() if row[7] is not None else None
            notes         = str(row[8]).strip() if row[8] is not None else None

            deadline = self.extract_deadline(str(requirement) if requirement else "")
            is_recurring, recurrence_label = self.detect_recurring(
                str(requirement) if requirement else ""
            )
            staff_names = self.extract_staff_names(staff_text)
            status = "pending"

            doc = {
                "row_number": row_number,
                "received_date": received_date,
                "document_type": doc_type,
                "content_summary": content,
                "reference_number": reference,
                "requirement": requirement,
                "deadline": deadline,
                "is_recurring": is_recurring,
                "recurrence_label": recurrence_label,
                "status": status,
                "result": result,
                "notes": notes,
                "staff_names": staff_names
            }

            #always import the document regardless 
            documents.append(doc)

            #separately track which ones need admin attention
            if not deadline and not is_recurring:
                flagged.append({**doc, "flag_reason": "deadline not found"})

        return (documents, flagged)
    
    def parse_tab2(self, sheet, header_row: int = None) -> tuple:
        header_row = header_row or self.TAB2_HEADER_ROW
        directives = []
        flagged = []

        for row in sheet.iter_rows(min_row=header_row, values_only=True):
            if not any(row):
                continue

            row_number    = int(row[0]) if row[0] else None
            meeting_date  = self._parse_date(row[1])
            content       = str(row[2]).strip() if row[2] is not None else None
            staff_text    = str(row[3]).strip() if row[3] is not None else None
            deadline_text = str(row[4]).strip() if row[4] is not None else None
            result        = str(row[5]).strip() if row[5] is not None else None
            notes         = str(row[6]).strip() if row[6] is not None else None

            # detect recurring first
            is_recurring, recurrence_label = self.detect_recurring(
                str(deadline_text) if deadline_text else ""
            )

            # only extract deadline if not recurring
            if is_recurring:
                deadline = None
            else:
                deadline = self.extract_deadline(deadline_text)

            staff_names = self.extract_staff_names(staff_text)
            status = "pending"

            directive = {
                "row_number": row_number,
                "meeting_date": meeting_date,
                "directive_content": content,
                "deadline": deadline,
                "is_recurring": is_recurring,
                "recurrence_label": recurrence_label,
                "status": status,
                "result": result,
                "notes": notes,
                "staff_names": staff_names
            }

            directives.append(directive)
            if not deadline and not is_recurring:
                flagged.append({**directive, "flag_reason": "deadline not found"})
                
        return (directives, flagged)

    def parse(self, tab1_name: str, tab2_name: str, tab1_header_row: int = None, tab2_header_row: int = None) -> dict:
        sheet1 = self.wb[tab1_name]
        sheet2 = self.wb[tab2_name]

        documents, flagged_docs = self.parse_tab1(sheet1, tab1_header_row)
        directives, flagged_dirs = self.parse_tab2(sheet2, tab2_header_row)

        #collect all unique staff names from both tabs
        all_staff = set()
        for doc in documents + flagged_docs:
            for name in doc.get("staff_names", []):
                all_staff.add(name)

        for directive in directives + flagged_dirs:
            for name in directive.get("staff_names", []):
                all_staff.add(name)

        return {
            "documents": documents,
            "directives": directives,
            "flagged": flagged_docs + flagged_dirs,
            "staff": list(all_staff),
            "summary": {
                "documents_parsed": len(documents),
                "directives_parsed": len(directives),
                "total_flagged": len(flagged_docs + flagged_dirs),
                "staff_found": len(all_staff)
            }
        }