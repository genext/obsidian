---
title: "August 12th, 2024"
created: 2024-08-12 09:09:06
updated: 2024-08-12 21:01:56
---
  * 오늘 할 일
    * 업무 메일 확인
    * 신청자 다운로드, 수혜자 업로드 및 DB 저장 개발

  * 명경지수
  * 10:57 테이블명 정하는 데 있어서 기존 테이블과 혼동되는 것을 피하기 위해 바우처 프로젝트하면서 새로 생성한 테이블에 VOUCH를 붙여서 통일하기로 함.
    * TB_CSTMR_RCRIT -> TB_VOUCH_CSTMR_RCRIT
    * TB_INDUTY_CD -> TB_VOUCH_INDUTY_CD
    * TB_VOUCH_INDUTY -> TB_VOUCH_INDUTY_RL
    * TB_INSTT -> TB_VOUCH_INSTT
    * TB_INSTT_EMP -> TB_VOUCH_INSTT_EMP
    * TB_PLACE -> TB_VOUCH_PLACE
    * TB_PLACE_EMP -> TB_VOUCH_PLACE_EMP
    * TB_VOUCH_PLACE -> TB_VOUCH_PLACE_RL
      * foreign key 수정
  * 11:45 2개비
  * 15:09 파일 다운로드 개발 중. 기존 소스는 바로 다운로드하는 기능이 없다. 
  * 16:47 겨우 만들긴 했는데 headerList.Length가 0. 이걸 고쳐야 한다.
    * DB 조회 데이터
      * ```plain text
applcntList: [TbVcApplcnt{reqstYn='Y', bankCd='NHB', walletAdres='wallet', reqstDt=Thu Aug 01 00:00:00 KST 2024, processDt=Mon Aug 05 00:00:00 KST 2024}, TbVcApplcnt{reqstYn='Y', bankCd='NHB', walletAdres='wallet', reqstDt=Thu Aug 01 00:00:00 KST 2024, processDt=Mon Aug 05 00:00:00 KST 2024}, TbVcApplcnt{reqstYn='N', bankCd='NHB', walletAdres='wallet', reqstDt=Thu Aug 01 00:00:00 KST 2024, processDt=Mon Aug 05 00:00:00 KST 2024}]```
  * 18:41 겨우 엑셀 다운로드를 하긴 했는데 front-end에 이미 있는 것을 유승헌 부장님이 확인해줬다. 아이고...이게 뭔 시간 낭비였나..어쨌든 백엔드에서 하는 방법도 있다는 것을 알게 된 것을 소득으로 생각하자.
    * rest controller endpoint - 화면에만 표시하는 것과 엑셀만 받는 것 두 개
      * ```java
 /**
     * 특정 바우처 신청자 목록 조회
     * @throws Exception
     */
    @Operation(summary = "바우처 신청자 목록 조회", description = "특정 바우처에 대한 신청자 목록을 조회한다.")
    @GetMapping("/applcnt")
    public ResponseEntity<List<TbVcApplcnt>> selectRecruitApplcntInfo(
            @RequestParam(value = "vouchId", required = true) String vouchId) throws Exception
    {
        List<TbVcApplcnt> tbVcApplcntInfoList = tbVcRecruitServiceImpl.selectApplcnt(vouchId);
        return ResponseEntity.ok(tbVcApplcntInfoList);
    }

    @Operation(summary = "바우처 신청자 목록 엑셀 다운로드", description = "바우처 신청자 목록을 엑셀 파일로 다운로드합니다.",
        responses = {
                @ApiResponse(description = "엑셀 파일 다운로드", content = @Content(mediaType = "application/octet-stream"))
        })
    @PostMapping(path = "/downloadExcel", consumes = "application/json")
    public ResponseEntity<byte []> downloadExcel(
            @io.swagger.v3.oas.annotations.parameters.RequestBody(
                    description = "GridRequest for filtering and configuring the Excel download",
                    content = @Content(mediaType = "application/json",
                            schema = @Schema(example = """
                            {
                                "progressKey": "123456",
                                "paging": {
                                    "recordCountPerPage": 10,
                                    "pageListCount": 10,
                                    "currentPageNo": 1,
                                    "totalRecordCount": 8
                                },
                                "search": {
                                    "vouchId": "0000-0000-0000"
                                },
                                "excel": {
                                    "download": true,
                                    "fileType": "xlsx",
                                    "headerList": [],
                                    "columnList": [
                                        {
                                            "name": "VOUCH_NM",
                                            "title": "Voucher Name"
                                        },
                                        {
                                            "name": "KOREAN_NM",
                                            "title": "Korean Name"
                                        },
                                        {
                                            "name": "REQST_YN",
                                            "title": "Request Status"
                                        },
                                        {
                                            "name": "BANK_CD",
                                            "title": "Bank Code"
                                        },
                                        {
                                            "name": "WALLET_ADRES",
                                            "title": "Wallet Address"
                                        },
                                        {
                                            "name": "REQST_DT",
                                            "title": "Request Date"
                                        },
                                        {
                                            "name": "PROCESS_DT",
                                            "title": "Process Date"
                                        }
                                    ],
                                    "dataList": []
                                }
                            }
                            """))
            ) @RequestBody GridRequest gridRequest) throws IOException {
        if (ObjectUtils.isEmpty(gridRequest.getSearch().get("vouchId"))) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(null);
        }

        List<TbVcApplcnt> applcntList = tbVcRecruitServiceImpl.selectApplcnt(gridRequest.getSearch().get("vouchId").toString());

        logger.debug(("-------------------------------------------------------------------------------"));
        logger.debug("applcntList: {}", applcntList);
        // Validate and initialize the ExcelDownload configuration
        if (gridRequest.getExcel() == null || gridRequest.getExcel().getColumnList() == null || gridRequest.getExcel().getColumnList().length == 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(null);
        }

        // Use GridDataWriterToExcelWithPOI to generate the Excel file (same as before)
        GridDataWriterToExcelWithPOI excelWriter = new GridDataWriterToExcelWithPOI(gridRequest);
        excelWriter.writeStart();
        for (TbVcApplcnt applcnt : applcntList) {
            Map<String, Object> rowData = convertObjectToMap(applcnt);
            excelWriter.writeRowData(rowData);
        }
        excelWriter.writeEnd(true);

        byte[] excelData = excelWriter.getExcelData();

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDispositionFormData("attachment", "applcnt_data.xlsx");

        return new ResponseEntity<>(excelData, headers, HttpStatus.OK);
    }
```
    * 엑셀 다운로드 관련 라이브러리. 처음에만 파일을 다른 서버에 두고 Url을 통해 받는 것만 있었지만 바로 다운로드 받는 것도 추가. FileOutputStream만 있었지만 이것을 OutputStream으로 바꿈.
      * ```java
package kr.or.cbdc.infrastructure.grid.handler;

import java.io.*;
import java.text.ParseException;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import org.apache.commons.lang.exception.ExceptionUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.time.DateUtils;
import org.apache.poi.ss.usermodel.BorderStyle;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.CellStyle;
import org.apache.poi.ss.usermodel.DataFormat;
import org.apache.poi.ss.usermodel.FillPatternType;
import org.apache.poi.ss.usermodel.HorizontalAlignment;
import org.apache.poi.ss.usermodel.IndexedColors;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.VerticalAlignment;
import org.apache.poi.ss.util.CellRangeAddress;
import org.apache.poi.xssf.streaming.SXSSFWorkbook;
import org.apache.poi.xssf.usermodel.XSSFFont;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BaseException;
import kr.or.cbdc.infrastructure.framework.core.support.collection.BaseMap;
import kr.or.cbdc.infrastructure.framework.core.support.collection.ValueConverter;
import kr.or.cbdc.infrastructure.framework.core.support.io.util.IOUtil;
import kr.or.cbdc.infrastructure.grid.model.DataCellMergeInfo;
import kr.or.cbdc.infrastructure.grid.model.GridRequest;
import kr.or.cbdc.infrastructure.util.ExcelUtil;

public class GridDataWriterToExcelWithPOI extends GridDataWriterToExcel {

    private static final Logger log = LoggerFactory.getLogger(GridDataWriterToExcelWithPOI.class);

    private SXSSFWorkbook workbook;
    private Sheet sheet;
    private Set<String> mergedStartCell;
    private Map<Integer, DataCellMergeInfo> dataCellMergeInfoMap;

    public GridDataWriterToExcelWithPOI(GridRequest gridRequest) {
        super(gridRequest);
    }

    @Override
    public void writeStart() {
        this.workbook = new SXSSFWorkbook(100);

        this.workbook.setCompressTempFiles(true);

        for (int c = 0; c < this.columnList.length; c++) {
            String name = this.columnList[c].getName();
            String align = this.columnList[c].getAlign();
            String formatter = this.columnList[c].getFormatter();

            CellStyle cellStyle = this.workbook.createCellStyle();
            cellStyle.setVerticalAlignment(VerticalAlignment.CENTER);
            cellStyle.setBorderTop(BorderStyle.THIN);
            cellStyle.setBorderRight(BorderStyle.THIN);
            cellStyle.setBorderBottom(BorderStyle.THIN);
            cellStyle.setBorderLeft(BorderStyle.THIN);

            if (StringUtils.equals(align, "center")) {
                cellStyle.setAlignment(HorizontalAlignment.CENTER);
            } else if (StringUtils.equals(align, "right")) {
                cellStyle.setAlignment(HorizontalAlignment.RIGHT);
            }

            XSSFFont cellFont = (XSSFFont) this.workbook.createFont();
            cellFont.setFontName("Arial");
            cellFont.setFontHeightInPoints((short) 9);
            cellStyle.setFont(cellFont);

            DataFormat dataFormat = this.workbook.createDataFormat();

            if (StringUtils.equalsIgnoreCase(name, "_RN_")) {
                cellStyle.setFillForegroundColor(IndexedColors.GREY_25_PERCENT.index);
                cellStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
                cellStyle.setAlignment(HorizontalAlignment.CENTER);
                cellStyle.setDataFormat(dataFormat.getFormat("#"));
                for (BaseMap header : this.headerList) {
                    header.put(name, "No");
                }
                this.columnList[c].setWidth(45);
            } else if (StringUtils.equals(formatter, "number")) {
                //숫자 → 일반으로
                /*
                int decimalPlaces = this.columnList[c].getDecimalPlaces();
                if (decimalPlaces > 0) {
                    cellStyle.setDataFormat(
                            dataFormat.getFormat("###0." + StringUtils.leftPad("0", decimalPlaces, '0')));
                } else {
                    cellStyle.setDataFormat(dataFormat.getFormat("###,0"));
                }
                */
            } else if (StringUtils.equals(formatter, "date")) {
                cellStyle.setDataFormat(dataFormat.getFormat("yyyy-MM-dd"));
            } else if (StringUtils.equals(formatter, "datetime")) {
                cellStyle.setDataFormat(dataFormat.getFormat("yyyy-MM-dd HH:mm:ss"));
            }else{
                cellStyle.setWrapText(true);
            }

            this.columnList[c].setCellStyle(cellStyle);
        }
        this.sheet = this.createSheet();
    }

    @Override
    public void writeRowData(Map<String, Object> rowData) {
        int rowCount = this.sheet.getPhysicalNumberOfRows();

        Row row = this.sheet.createRow(rowCount);

        row.setHeight((short) (13 * 20));

        for (int c = 0; c < this.columnList.length; c++) {
            String name = this.columnList[c].getName();
            String formatter = this.columnList[c].getFormatter();
            Object value = this.getMapValue(rowData, name);

            Cell cell = row.createCell(c);

            cell.setCellStyle((CellStyle)this.columnList[c].getCellStyle());

            if (value == null || "".equals(value)) {
                cell.setCellValue("");
            } else if (StringUtils.equalsIgnoreCase(name, "_RN_")) {
                cell.setCellValue(value instanceof Integer ? (Integer) value : Integer.parseInt(value.toString(), 10));
            } else if (StringUtils.equals(formatter, "number")) {
                cell.setCellValue(ValueConverter.getDouble(value));
            } else if (StringUtils.equals(formatter, "date") || StringUtils.equals(formatter, "datetime")) {
                if (value instanceof Date) {
                    cell.setCellValue(ValueConverter.getDate(value));
                } else {
                    String dateStr = ValueConverter.getString(value);

                    if (dateStr.length() == 8) {
                        try {
                            cell.setCellValue(DateUtils.parseDate(dateStr, "yyyyMMdd"));
                        } catch (ParseException e) {
                            cell.setCellValue(dateStr);
                        }
                    } else {
                        cell.setCellValue(dateStr);
                    }
                }
            } else {
                cell.setCellValue(ValueConverter.getString(value));
            }
        }

        this.addDataCellMergedRegion(row.getRowNum());

        if (rowCount >= Math.pow(2, 20) - 1) {
            this.sheet = this.createSheet();
        }
    }

    @Override
    public void writeEnd(boolean success) {
        this.addDataCellMergedRegion();

//        FileOutputStream fos = null;
        OutputStream outputStream = null;
        try {
            if (this.gridRequest.getExcel().getWorkbookFile() != null) {
                outputStream = new FileOutputStream(this.gridRequest.getExcel().getWorkbookFile());
            } else {
                outputStream = new ByteArrayOutputStream();
            }
            this.workbook.write(outputStream);
        }
        /*
        catch (FileNotFoundException e) {
            this.deleteWorkbookFile();
            throw new BaseException(e);
         } */
        catch (IOException e) {
            this.deleteWorkbookFile();
            throw new BaseException(e);
        } finally {
            IOUtil.closeQuietly(outputStream);

//            if (!success) {
              if (!success && this.gridRequest.getExcel().getWorkbookFile() != null) {
                this.deleteWorkbookFile();
            }
            //this.workbook.dispose();
        }
    }

    // 엑셀 직접 다운로드를 위해 추가
    public byte[] getExcelData() throws IOException {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        this.workbook.write(bos);
        bos.close();
        this.workbook.dispose();
        return bos.toByteArray();
    }

    private Sheet createSheet() {
        this.addDataCellMergedRegion();

        Sheet sheet = this.workbook.createSheet("Sheet" + (this.workbook.getNumberOfSheets() + 1));

        CellStyle headerStyle = this.workbook.createCellStyle();
        headerStyle.setVerticalAlignment(VerticalAlignment.CENTER);
        headerStyle.setBorderTop(BorderStyle.THIN);
        headerStyle.setBorderRight(BorderStyle.THIN);
        headerStyle.setBorderBottom(BorderStyle.THIN);
        headerStyle.setBorderLeft(BorderStyle.THIN);
        headerStyle.setAlignment(HorizontalAlignment.CENTER);
        headerStyle.setFillForegroundColor(IndexedColors.GREY_25_PERCENT.index);
        headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);

        XSSFFont headerFont = (XSSFFont) this.workbook.createFont();
        headerFont.setFontName("Arial");
        headerFont.setFontHeightInPoints((short) 9);
        headerFont.setBold(true);
        headerStyle.setFont(headerFont);

//        int headerRows = this.headerList.length;
        int headerRows = (this.headerList != null && this.headerList.length > 0) ? this.headerList.length : 1;
        int headerCols = this.columnList.length;
        Integer colSplit = this.gridRequest.getExcel().getColSplit();

        if (colSplit == null || colSplit <= 0) {
            colSplit = this.getRnColumnIndex() + 1;
        }

        sheet.setDisplayGridlines(false);
        sheet.createFreezePane(colSplit, headerRows);

        if (this.headerList != null && this.headerList.length > 0) {
            for (int r = 0; r < headerRows; r++) {
                int mergeStartCol = 0;

                for (int c = 1; c < headerCols; c++) {
                    if (StringUtils.equals(this.getHeaderName(r, c), this.getHeaderName(r, mergeStartCol))) {
                        continue;
                    }

                    if (mergeStartCol != c - 1) {
                        CellRangeAddress cellRangeAddress = new CellRangeAddress(r, r, mergeStartCol, c - 1);
                        this.addMergedRegion(sheet, cellRangeAddress);
                    }

                    mergeStartCol = c;
                }

                if (mergeStartCol != headerCols - 1) {
                    CellRangeAddress cellRangeAddress = new CellRangeAddress(r, r, mergeStartCol, headerCols - 1);
                    this.addMergedRegion(sheet, cellRangeAddress);
                }
            }

            for (int c = 0; c < headerCols; c++) {
                int mergeStartRow = 0;

                for (int r = 1; r < headerRows; r++) {
                    if (StringUtils.equals(this.getHeaderName(r, c), this.getHeaderName(mergeStartRow, c))) {
                        continue;
                    }

                    if (mergeStartRow != r - 1) {
                        CellRangeAddress cellRangeAddress = new CellRangeAddress(mergeStartRow, r - 1, c, c);
                        this.addMergedRegion(sheet, cellRangeAddress);
                    }

                    mergeStartRow = r;
                }

                if (mergeStartRow != headerRows - 1) {
                    CellRangeAddress cellRangeAddress = new CellRangeAddress(mergeStartRow, headerRows - 1, c, c);
                    this.addMergedRegion(sheet, cellRangeAddress);
                }
            }
        }
        else {
            // Handle case when headerList is empty or null (generate headers using columnList)
            Row headerRow = sheet.createRow(0);
            headerRow.setHeight((short) (15 * 20));

            for (int c = 0; c < headerCols; c++) {
                Cell cell = headerRow.createCell(c);
                String headerTitle = this.columnList[c].getTitle() != null ? this.columnList[c].getTitle() : this.columnList[c].getName();  // Use title or fallback to name
                cell.setCellValue(headerTitle);  // Assuming getTitle() method provides the header title
                cell.setCellStyle(headerStyle);
            }
        }


        for (int c = 0, cc = this.columnList.length; c < cc; c++) {
            int columnWidth = (this.columnList[c].getWidth() != null) ? this.columnList[c].getWidth() : 100;  // Default to 10 if width is null
            sheet.setColumnWidth(c, columnWidth * 35);
            boolean hidden = (this.columnList[c].getHidden() != null) ? this.columnList[c].getHidden() : false;
            sheet.setColumnHidden(c, hidden);
        }

        return sheet;
    }

    private void addDataCellMergedRegion(int rowNum) {
        if (this.sheet == null) {
            return;
        }

        Integer colSplit = this.gridRequest.getExcel().getColSplit();

        if (colSplit == null || colSplit <= 1) {
            return;
        }

        if (this.dataCellMergeInfoMap == null) {
            this.dataCellMergeInfoMap = new HashMap<Integer, DataCellMergeInfo>();
        }

        int rnColIndex = this.getRnColumnIndex();
        Row row = this.sheet.getRow(rowNum);

        for (int c = rnColIndex + 1; c < colSplit - 1; c++) {
            String currCellValue = this.getAllCellValue(row, c);

            DataCellMergeInfo dataCellMergeInfo = this.dataCellMergeInfoMap.get(c);

            if (dataCellMergeInfo == null) {
                dataCellMergeInfo = new DataCellMergeInfo(rowNum, currCellValue);
                this.dataCellMergeInfoMap.put(c, dataCellMergeInfo);
            }

            if (StringUtils.equals(currCellValue, dataCellMergeInfo.getMergeValue())) {
                continue;
            }

            if (dataCellMergeInfo.getMergeStartRow() != rowNum - 1) {
                CellRangeAddress cellRangeAddress = new CellRangeAddress(dataCellMergeInfo.getMergeStartRow(),
                        rowNum - 1, c, c);
                this.addMergedRegion(this.sheet, cellRangeAddress);
            }

            dataCellMergeInfo.reset(rowNum, currCellValue);
        }
    }

    private void addDataCellMergedRegion() {
        if (this.sheet == null) {
            return;
        }

        Integer colSplit = this.gridRequest.getExcel().getColSplit();

        if (colSplit == null || colSplit <= 1) {
            return;
        }

        if (this.dataCellMergeInfoMap == null) {
            this.dataCellMergeInfoMap = new HashMap<Integer, DataCellMergeInfo>();
        }

        int rnColIndex = this.getRnColumnIndex();

        for (int c = rnColIndex + 1; c < colSplit - 1; c++) {
            DataCellMergeInfo dataCellMergeInfo = this.dataCellMergeInfoMap.get(c);

            if (dataCellMergeInfo.getMergeStartRow() != this.sheet.getLastRowNum()) {
                CellRangeAddress cellRangeAddress = new CellRangeAddress(dataCellMergeInfo.getMergeStartRow(),
                        this.sheet.getLastRowNum(), c, c);
                this.addMergedRegion(this.sheet, cellRangeAddress);
            }
        }
    }

    private String getAllCellValue(Row row, int colIndex) {
        int rnColIndex = this.getRnColumnIndex();
        StringBuilder sb = new StringBuilder();

        for (int i = rnColIndex + 1; i <= colIndex; i++) {
            sb.append("$||$").append(ExcelUtil.getCellValue(row.getCell(i))).append("$||$");
        }

        return sb.toString();
    }

    private void addMergedRegion(Sheet sheet, CellRangeAddress cellRangeAddress) {
        if (this.mergedStartCell == null) {
            this.mergedStartCell = new HashSet<String>();
        }

        String startCell = cellRangeAddress.getFirstColumn() + ":" + cellRangeAddress.getFirstRow();

        if (this.mergedStartCell.contains(startCell)) {
            return;
        }

        this.mergedStartCell.add(startCell);

        try {
            sheet.addMergedRegion(cellRangeAddress);
        } catch (RuntimeException e) {
            if (log.isErrorEnabled()) {
                log.warn("엑셀 머지 에러 : {} => {}", cellRangeAddress, ExceptionUtils.getRootCauseMessage(e));
            }
        }
    }

}
```
    * GridRequest
      * ```java
package kr.or.cbdc.infrastructure.grid.model;

import java.io.File;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import kr.or.cbdc.infrastructure.framework.core.persistence.dao.paging.model.PagingInfo;
import kr.or.cbdc.infrastructure.framework.core.support.collection.BaseMap;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class GridRequest {
    private String progressKey;
    private PagingInfo paging;
    private BaseMap search;
    private Option option;
    private ExcelDownload excel;

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Option {
        private boolean testMode;
        private String dateFormat;
        private String timestampFormat;
    }

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ExcelDownload {
        private Boolean download;
        private String fileType;
        private BaseMap[] headerList;
        private GridExcelColumn[] columnList;
        private List<BaseMap> dataList;
        private Integer colSplit;
        private File workbookFile;
    }
}```
    * GridExcelColumn
      * ```java
package kr.or.cbdc.infrastructure.grid.model;

import org.apache.commons.lang3.BooleanUtils;
import org.apache.poi.ss.usermodel.CellStyle;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import lombok.Data;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class GridExcelColumn {

    private String name;
    private String align;
    private String formatter;
    private Integer width;
    private Boolean hidden;
    private Integer decimalPlaces;
    // private CellStyle cellStyle;
    private Object cellStyle;
    private String title;
}
```