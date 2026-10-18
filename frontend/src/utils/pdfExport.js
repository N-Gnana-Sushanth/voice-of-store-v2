import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

/**
 * Generate and download a professional PDF report for Issue Analysis.
 *
 * @param {Object} options
 * @param {Array} options.issues - List of issue records (respects active filters)
 * @param {string} options.reportingPeriod - e.g. "Week of 12 Oct - 18 Oct 2026"
 * @param {string} options.selectedCategory - Currently active category filter or null
 * @param {string} options.selectedRegion - Active region filter e.g. "All Regions"
 * @param {Object} options.user - Current user profile
 * @param {Array} [options.categorySummary] - Optional category counts for summary
 * @param {Array} [options.severitySummary] - Optional severity counts for summary
 */
export function generateIssueAnalysisPdf({
  issues = [],
  reportingPeriod = null,
  selectedDate = null,
  selectedCategory = null,
  selectedRegion = 'All Regions',
  user = { name: 'Sushanth', role: 'HQ Analyst' },
  categorySummary = [],
  severitySummary = [],
}) {
  const effectivePeriod = reportingPeriod || selectedDate || 'Week of 12 Oct - 18 Oct 2026';
  try {
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 14;

    // Brand Green palette
    const primaryColor = [5, 150, 105]; // #059669
    const primaryDark = [4, 120, 87];   // #047857
    const textDark = [15, 23, 42];      // #0f172a
    const textMuted = [100, 116, 139];  // #64748b
    const bgLight = [241, 247, 244];    // #f1f7f4
    const borderMint = [187, 247, 208]; // #bbf7d0

    let currentY = 14;

    // 1. Top Decorative Brand Bar
    doc.setFillColor(...primaryColor);
    doc.rect(0, 0, pageWidth, 5, 'F');

    // 2. Header Title & Brand Name
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(18);
    doc.setTextColor(...primaryDark);
    doc.text('Voice of Store', margin, currentY + 4);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.setTextColor(...textMuted);
    doc.text('Operational Intelligence & Incident Resolution Platform', margin, currentY + 9);

    // Document Type Label (Right aligned)
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(14);
    doc.setTextColor(...textDark);
    doc.text('Issue Analysis Report', pageWidth - margin, currentY + 4, { align: 'right' });

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.setTextColor(...textMuted);
    const generatedAt = new Date().toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
    doc.text(`Generated: ${generatedAt}`, pageWidth - margin, currentY + 9, { align: 'right' });

    currentY += 16;

    // Divider line
    doc.setDrawColor(...borderMint);
    doc.setLineWidth(0.5);
    doc.line(margin, currentY, pageWidth - margin, currentY);

    currentY += 6;

    // 3. Metadata & Context Summary Box
    doc.setFillColor(...bgLight);
    doc.roundedRect(margin, currentY, pageWidth - (margin * 2), 22, 2, 2, 'F');
    doc.setDrawColor(...borderMint);
    doc.roundedRect(margin, currentY, pageWidth - (margin * 2), 22, 2, 2, 'S');

    doc.setFontSize(9);
    const colWidth = (pageWidth - (margin * 2)) / 4;

    // Meta Column 1: Reporting Period
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...textMuted);
    doc.text('REPORTING PERIOD', margin + 4, currentY + 6);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...textDark);
    const safePeriod = doc.splitTextToSize(effectivePeriod, colWidth - 6);
    doc.text(safePeriod[0] || 'Current Period', margin + 4, currentY + 12);

    // Meta Column 2: Region Filter
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...textMuted);
    doc.text('REGION FILTER', margin + colWidth + 4, currentY + 6);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...textDark);
    const safeRegion = doc.splitTextToSize(selectedRegion || 'All Regions', colWidth - 6);
    doc.text(safeRegion[0] || 'All Regions', margin + colWidth + 4, currentY + 12);

    // Meta Column 3: Category Filter
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...textMuted);
    doc.text('CATEGORY FILTER', margin + (colWidth * 2) + 4, currentY + 6);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...primaryDark);
    const safeCategory = selectedCategory ? selectedCategory : 'All Categories';
    doc.text(safeCategory, margin + (colWidth * 2) + 4, currentY + 12);

    // Meta Column 4: Prepared By
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...textMuted);
    doc.text('PREPARED BY', margin + (colWidth * 3) + 4, currentY + 6);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...textDark);
    doc.text(`${user?.name || 'Sushanth'} (${user?.role || 'HQ Analyst'})`, margin + (colWidth * 3) + 4, currentY + 12);

    currentY += 28;

    // 4. Key Metrics Executive Summary Cards
    const totalIssues = issues.length;
    const highCount = issues.filter((i) => (i.severity || '').toLowerCase() === 'high' || (i.severity || '').toLowerCase() === 'critical').length;
    const medCount = issues.filter((i) => (i.severity || '').toLowerCase() === 'medium').length;
    const lowCount = issues.filter((i) => (i.severity || '').toLowerCase() === 'low').length;

    const summaryCards = [
      { label: 'Total Filtered Issues', value: totalIssues.toString(), color: primaryDark },
      { label: 'High / Critical Severity', value: highCount.toString(), color: [225, 29, 72] }, // Red
      { label: 'Medium Severity', value: medCount.toString(), color: [180, 83, 9] },   // Amber
      { label: 'Low Severity', value: lowCount.toString(), color: [21, 128, 61] },     // Green
    ];

    const cardGap = 4;
    const cardWidth = (pageWidth - (margin * 2) - (cardGap * 3)) / 4;
    const cardHeight = 16;

    summaryCards.forEach((c, idx) => {
      const cardX = margin + idx * (cardWidth + cardGap);
      doc.setFillColor(255, 255, 255);
      doc.setDrawColor(226, 232, 240);
      doc.roundedRect(cardX, currentY, cardWidth, cardHeight, 1.5, 1.5, 'FD');

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(7.5);
      doc.setTextColor(...textMuted);
      doc.text(c.label, cardX + 3, currentY + 5);

      doc.setFont('helvetica', 'bold');
      doc.setFontSize(12);
      doc.setTextColor(...c.color);
      doc.text(c.value, cardX + 3, currentY + 12);
    });

    currentY += cardHeight + 8;

    // 5. Section Heading: Detailed Incident Breakdown
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    doc.setTextColor(...textDark);
    doc.text('Issue Breakdown & Evidence Analysis', margin, currentY);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8.5);
    doc.setTextColor(...textMuted);
    const subtitle = selectedCategory
      ? `Showing ${totalIssues} issue(s) filtered by category "${selectedCategory}"`
      : `Showing ${totalIssues} ranked issue(s) across operations`;
    doc.text(subtitle, margin + 78, currentY);

    currentY += 4;

    // 6. Detailed Table using autoTable
    if (issues.length === 0) {
      doc.setFillColor(248, 250, 252);
      doc.roundedRect(margin, currentY, pageWidth - (margin * 2), 20, 2, 2, 'F');
      doc.setFont('helvetica', 'italic');
      doc.setFontSize(10);
      doc.setTextColor(...textMuted);
      doc.text('No issues match the selected filter criteria for this reporting period.', pageWidth / 2, currentY + 11, { align: 'center' });
      currentY += 26;
    } else {
      const tableHeaders = ['#', 'Issue Title', 'Category', 'Severity', 'Stores', 'Owner', 'Evidence Excerpt'];

      const tableRows = issues.map((item, idx) => {
        // Sanitize strings for PDF font compatibility
        const cleanText = (str) => (str ? String(str).replace(/[^\x00-\x7F]/g, ' ') : '');
        return [
          item.id || idx + 1,
          cleanText(item.title || 'Untitled Issue'),
          cleanText(item.category || 'General'),
          cleanText(item.severity || 'Medium'),
          cleanText(item.affectedStores || '1 store'),
          cleanText(item.owner || 'Store Ops'),
          cleanText(item.evidence ? `"${item.evidence}"` : 'No excerpt recorded'),
        ];
      });

      autoTable(doc, {
        startY: currentY,
        head: [tableHeaders],
        body: tableRows,
        margin: { left: margin, right: margin, bottom: 18 },
        theme: 'striped',
        headStyles: {
          fillColor: primaryColor,
          textColor: [255, 255, 255],
          fontSize: 8.5,
          fontStyle: 'bold',
          halign: 'left',
          cellPadding: 2.5,
        },
        bodyStyles: {
          fontSize: 8,
          textColor: textDark,
          cellPadding: 2.5,
          valign: 'top',
        },
        alternateRowStyles: {
          fillColor: [248, 250, 252],
        },
        columnStyles: {
          0: { cellWidth: 8, halign: 'center' },      // #
          1: { cellWidth: 38, fontStyle: 'bold' },    // Issue Title
          2: { cellWidth: 26 },                       // Category
          3: { cellWidth: 18, halign: 'center' },     // Severity
          4: { cellWidth: 22 },                       // Stores
          5: { cellWidth: 26 },                       // Owner
          6: { cellWidth: 'auto', fontStyle: 'italic' }, // Evidence
        },
        didParseCell: (data) => {
          // Color code severity column
          if (data.section === 'body' && data.column.index === 3) {
            const val = String(data.cell.raw).toLowerCase();
            if (val.includes('high') || val.includes('critical')) {
              data.cell.styles.textColor = [225, 29, 72];
              data.cell.styles.fontStyle = 'bold';
            } else if (val.includes('medium')) {
              data.cell.styles.textColor = [180, 83, 9];
              data.cell.styles.fontStyle = 'bold';
            } else if (val.includes('low')) {
              data.cell.styles.textColor = [21, 128, 61];
            }
          }
        },
        didDrawPage: (data) => {
          // Footer on every page
          const str = `Page ${doc.internal.getNumberOfPages()}`;
          doc.setFont('helvetica', 'normal');
          doc.setFontSize(8);
          doc.setTextColor(...textMuted);
          doc.text('Voice of Store — Confidential Operational Report', margin, pageHeight - 8);
          doc.text(str, pageWidth - margin, pageHeight - 8, { align: 'right' });
        },
      });
    }

    // 7. Save and trigger browser download
    const filename = `Voice-of-Store-Issue-Analysis-Report.pdf`;
    doc.save(filename);
    return { success: true, filename };
  } catch (error) {
    console.error('Failed to generate Issue Analysis PDF:', error);
    throw error;
  }
}
