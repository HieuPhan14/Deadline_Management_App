import openpyxl
import re
from rapidfuzz import fuzz
from dateutil.parser import parse as parse_date
from dateutil.parser import ParserError

class ExcelParser:
    TAB1_HEADER_ROW = 6 # data starts at row 6 in Tab 1
    TAB2_HEADER_ROW = 9 # data starts at row 9 in Tab 2

    def __init__(self, file):
        self.wb = openpyxl.load_workbook(file)

    def detect_tabs(self) -> dict:
        return {
            "sheet_names": self.wb.sheetnames,
            "suggested": {
                "tab1": self._suggest_tab("theo doi cv"),
                "tab2": self._suggest_tab("chi dao ldp")
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
        return [name.strip() for name in names if name.strip()]

    def detect_recurring(self, text: str) -> tuple:
        if not text:
            return (False, None)

        recurring_keywords = {
            "mỗi ngày", "hàng ngày", "hàng tuần",
            "hàng tháng", "thường xuyên"
        } 
        text_lower = str(text).lower()

        for keyword in recurring_keywords:
            if keyword in text_lower:
                return (True, str(text).strip())

        return (False, None)
    
    def extract_deadline(self, text: str):
        if not text:
            return None
        
        text = str(text)

        pattern = r'\d{1,2}/\d{1,2}/\d{4}'
        matches = re.findall(pattern, text)

        if matches:
            try:
                return parse_date(matches[-1], dayfirst=True).date()
            except ParserError:
                return None
            
        return None
    
    def parse_tab1(self, sheet) -> tuple:
        documents = []
        flagged = []

        #skip header rows, start at row 4
        for row in sheet.iter_rows(min_row=self.TAB1_HEADER_ROW, values_only=True):
            if not any(row):
                continue

            row_number    = row[0]
            received_date = row[1]
            doc_type      = row[2]
            content       = row[3]
            reference     = row[4]
            requirement   = row[5]  # some deadline in here
            staff_text    = row[6]
            result        = row[7]
            notes         = row[8]

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

            if not deadline and not is_recurring:
                flagged.append({**doc, "flag_reason": "deadline not found"})
            else:
                documents.append(doc)

        return (documents, flagged)
    
    def parse_tab2(self, sheet) -> tuple:
        directives = []
        flagged = []

        for row in sheet.iter_rows(min_row=self.TAB2_HEADER_ROW, values_only=True):
            if not any(row):
                continue

            row_number    = row[0]
            meeting_date  = row[1]
            content       = row[2]
            staff_text    = row[3]
            deadline_text = row[4]
            result        = row[5]
            notes         = row[6]

            # detect recurring first
            is_recurring, recurrence_label = self.detect_recurring(
                str(deadline_text) if deadline_text else ""
            )

            # only extract deadline if not recurring
            if is_recurring:
                deadline = None
            else:
                deadline = self.extract_deadline(
                    str(deadline_text) if deadline_text else ""
                )

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

            if not deadline and not is_recurring:
                flagged.append({**directive, "flag_reason": "deadline not found"})
            else:
                directives.append(directive)

        return (directives, flagged)

    def parse(self, tab1_name: str, tab2_name:str) -> dict:
        sheet1 = self.wb[tab1_name]
        sheet2 = self.wb[tab2_name]

        documents, flagged_docs = self.parse_tab1(sheet1)
        directives, flagged_dirs = self.parse_tab2(sheet2)

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