import os
from datetime import datetime
import copy

from django.template import Template, Context
from django.http import HttpResponse, HttpResponseRedirect

try:
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import BaseDocTemplate, PageTemplate, SimpleDocTemplate, Paragraph, Spacer, PageBreak, CondPageBreak, Frame, FrameBreak, NextPageTemplate
    from reportlab.platypus import Table as PDFTable
    from reportlab.platypus import TableStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.lib import colors 
    from reportlab.lib.pagesizes import A4, LETTER, landscape, portrait
    from reportlab.rl_config import defaultPageSize
    from reportlab.lib.units import inch
    PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
except ImportError:
    pass

class PDFReport():
    ''' 
    PDFReport Is a class that create table format reports
    The Title is placed on its own page for the first page 
    usage: 
            pdfrpt = PDFRrepot()
            pdfrpt.setLandscape(False)
            pdfrpt.setTitle("Title")
            pdfrpt.setTableData(queryset, fields, "Table Title")
            pdfrpt.setFilename("filename")
            pdfrpt.setNumOfColumns(2) # for two column setup
            pdfrpt.render()
    '''
    title = u"Report"
    pageinfo = ""
    filename = "report"
    styles = getSampleStyleSheet()
    data = []
    landscape = False
    hasfooter = False
    headers = []
    cols = 1
    PAGESIZE = A4
    fontSize = 8
    
    def __init__(self):
        self.headers.append("")
    
    def setLandscape(self, state):
        """ enable or disable landscape display
            @var state: True or False
        """
        self.landscape = state
    
    def enableFooter(self, state):
        """
        enable formatter for the last row of the table
        e.g for summaries have bold border lines
        @var state: True or False
        """
        self.hasfooter = state
        
    def setTitle(self, title):
        """ @var title: The Report Title """
        if title:
            self.title = title
           
    def setPageInfo(self, pageinfo):
        if pageinfo:
            self.pageinfo = pageinfo
               
    def setFilename(self, filename):
        """ @var filename: filename for the generated pdf document """
        if filename:
            self.filename = filename
    
               
    def setFontSize(self, size):
        """ @var size: font-size """
        if size:
            self.fontSize = size
                   
    def setNumOfColumns(self, cols):
        """ @var cols: number of columns """
        if cols:
            self.cols = cols
            
     
    def setPageBreak(self):
        """ force/add a page break """
        self.data.append(PageBreak())
        
    def setTableData(self, queryset, fields, title):        
        """
        set table data
        @var queryset: data
        @var fields: table column headings
        @var title: Table Heading
    """
        data = []
        header = False
        c = 0;
        #prepare the data
        for row in queryset:
            if not header:
                data.append([f["name"] for f in fields])
                header = True
            ctx = Context({"object": row })
            values = [ Template(h["bit"]).render(ctx) for h in fields ]
            data.append(values)
        
        table = PDFTable(data,None,None,None,1)
        #table rows n cols formatting
        ts = [
            ('ALIGNMENT', (0,0), (-1,-1), 'LEFT'),
            ('LINEBELOW', (0,0), (-1,-0), 2, colors.black),            
            ('LINEBELOW', (0,1), (-1,-1), 0.8, colors.lightgrey),
            ('FONT', (0,0), (-1, -1), "Times-Roman", self.fontSize),
            ('ROWBACKGROUNDS', (0,0), (-1, -1), [colors.whitesmoke, colors.white]),    
            ('LEFTPADDING', (0,0), (-1, -1), 1),
            ('RIGHTPADDING', (0,0), (-1, -1), 1),
            ('TOPPADDING', (0,0), (-1, -1), 1),
            ('BOTTOMPADDING', (0,0), (-1, -1), 1),        
        ]
        
        #last row formatting when required
        if self.hasfooter is True:
            ts.append(('LINEABOVE', (0,-1), (-1,-1), 1, colors.black))
            ts.append(('LINEBELOW', (0,-1), (-1,-1), 2, colors.black))
            ts.append(('LINEBELOW', (0,3), (-0,-0), 2, colors.green))             
            ts.append(('LINEBELOW', (0,-1), (-1,-1), 0.8, colors.lightgrey))
            ts.append(('FONT', (0,-1), (-1, -1), "Times-Roman", 7))
            
        table.setStyle(TableStyle(ts))

        table.hAlign = "LEFT"
        self.data.append(table)
        
        """
            The number of rows per page for two columns is about 90.
            using this information you can figure how many pages the
            table is going to overlap hence you place a header/subtitle
            in that position for it to be printed appropriately
        """
        c = len(queryset)/90
            
        if int(c)< c:
           c = int(c) + 1
               
           for i in range(c):
               self.headers.append(title)
        
    def render(self):
        elements = []
        
        self.styles['Title'].alignment = TA_LEFT
        self.styles['Title'].fontName = self.styles['Heading2'].fontName = "Times-Roman"
        self.styles["Normal"].fontName = "Times-Roman"
        self.styles["Normal"].fontSize = 7
        #self.styles["Normal"].fontWeight = "BOLD"
            
        filename = self.filename + datetime.now().strftime("%Y%m%d%H%M%S") + ".pdf"
        #doc = SimpleDocTemplate(filename)
                     
        #now create the title page
        elements.append(Paragraph(self.title, self.styles['Title']))
        
        #done with the title info, move to the next frame and queue up the later page template
        elements.append(FrameBreak())        
        elements.append(NextPageTemplate("laterPages"))
        elements.append(PageBreak())
        
        for data in self.data:
            elements.append(data)        
        
        if self.landscape is True:
            self.PAGESIZE = landscape(A4)
        doc = MultiColDocTemplate(filename, self.cols, pagesize=self.PAGESIZE, allowSplitting=1)
        doc.setTitle(self.title)
        doc.setHeaders(self.headers)        
        doc.build(elements)
        
        response = HttpResponse(mimetype='application/pdf')
        response['Cache-Control'] = ""
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        response.write(open(filename).read())
        os.remove(filename)
        return response
          
    # what should appear on the first page 
    def myFirstPage(self, canvas, doc):
        pageinfo = self.pageinfo
        canvas.saveState()
        '''canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo))
        '''
        textobject = canvas.beginText()
        textobject.setTextOrigin(inch, 0.75*inch)
        textobject.setFont("Times-Roman", 9)
        textobject.textLine("Page %d" % (doc.page))
        textobject.setFillGray(0.4)
        textobject.textLines(pageinfo)
        canvas.hAlign = "CENTER"
        canvas.drawText(textobject)
        canvas.restoreState()
    
    # what to do on other pages
    def myLaterPages(self, canvas, doc):
        pageinfo = self.pageinfo
        canvas.saveState()
        '''canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo))
        '''
        textobject = canvas.beginText()
        textobject.setTextOrigin(inch, 0.75*inch)
        textobject.setFont("Times-Roman", 9)
        textobject.textLine("Page %d" % (doc.page))
        textobject.setFillGray(0.4)
        textobject.textLines(pageinfo)
        canvas.hAlign = "CENTER"
        
class MultiColDocTemplate(BaseDocTemplate):
    "A multi column document template"
    headers = []
    title = u"Report Title Here"
    
    def __init__(self, filename, frameCount=1, **kw):
        """
            @FIXME: need to remove frameCount to maintain consistency with BaseDocTemplate constructor
                   and hence find a way to pass frameCount
        """
        apply(BaseDocTemplate.__init__,(self, filename), kw)
        
        self.addPageTemplates(self.firstPage())
        
        frameWidth = self.width/frameCount
        frameHeight = self.height-.5*inch
        frames = []
        for frame in range(frameCount):
            leftMargin = self.leftMargin + frame*frameWidth
            column = Frame(leftMargin, self.bottomMargin-.95*inch, frameWidth, frameHeight+1.75*inch,leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0)
            frames.append(column)
        
        template = PageTemplate(frames=frames, id="laterPages", onPage=self.addHeader)
        self.addPageTemplates(template)
    
    def firstPage(self):
        style = getSampleStyleSheet()
        #title page styles
        titleStyle = style["Title"]
        titleStyle.fontSize=40
        titleStyle.leading = titleStyle.fontSize*1.1
        #need to copy the object or style changes will apply to any incarnation of "Normal"
        subTitleStyle = copy.copy(style["Normal"])
        subTitleStyle.alignment=TA_CENTER
        subTitleStyle.fontName="Times-Roman"
        
        
        frameHeight = self.height-.5*inch
        frameWidth = self.width
        #title page frames
        firstPageHeight = 3.5*inch
        firstPageBottom = frameHeight-firstPageHeight
        framesFirstPage = []
        titleFrame = Frame(self.leftMargin, firstPageBottom, self.width, firstPageHeight)
        framesFirstPage.append(titleFrame)
        #columns for the first page
        firstPageColumn = Frame(self.leftMargin, self.bottomMargin, frameWidth, firstPageBottom)
        framesFirstPage.append(firstPageColumn)
        return PageTemplate(frames=framesFirstPage, id="firstPage")
                     
    def addHeader(self, canvas, document):
        """ display the heading of the page or document """
        canvas.saveState()
        title = self.getSubTitle(document.page-1)
        fontsize = 12
        fontname = 'Times-Roman'
        headerBottom = document.bottomMargin+document.height+document.topMargin/2
        bottomLine = headerBottom - fontsize/4
        topLine = headerBottom + fontsize
        lineLength = document.width+document.leftMargin
        canvas.setFont(fontname,fontsize)
        
        canvas.drawString(document.leftMargin, headerBottom, title)
        canvas.restoreState()
        
    def getTitle(self):
        return u"%s"%self.title
    
    def setTitle(self, title):
        if title:
            self.title = title
    
    def getSubTitle(self, pos):
        
        try:
            """ since subtitles vary from page to page, I pick the relevant
             title according to the page number """    
            return u"%s"%self.headers[pos]
        except:
            return u""
    
    def setHeaders(self, headers):
        self.headers = headers
        