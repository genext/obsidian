---
title: "August 9th, 2024"
created: 2024-08-09 06:49:07
updated: 2024-08-09 17:12:47
---
  * 06:45 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 바우처 모집대상 관리 개발

  * 명경지수
  * 07:01 어제 올렸다는 화면 확인하다가 에러 발견
    * 에러 2개. ReactDatePicker, setGridResult(response)
      * ```plain text
Compiled with problems:
×
ERROR in src/pages/vc/RecruitManagement/detail.tsx:111:24
TS2769: No overload matches this call.
  Overload 1 of 2, '(props: ReactDatePickerProps<undefined, undefined>): ReactDatePicker<undefined, undefined>', gave the following error.
    Property 'onChange' is missing in type '{}' but required in type 'Readonly<ReactDatePickerProps<undefined, undefined>>'.
  Overload 2 of 2, '(props: ReactDatePickerProps<undefined, undefined>, context: any): ReactDatePicker<undefined, undefined>', gave the following error.
    Property 'onChange' is missing in type '{}' but required in type 'Readonly<ReactDatePickerProps<undefined, undefined>>'.
    109 |                     <label className="hide">달력시작</label>
    110 |                     <div className="date-box">
  > 111 |                       <ReactDatePicker />
        |                        ==^====^====^==
    112 |                     </div>
    113 |                     <span> ~ </span>
    114 |                     <label className="hide">달력끝</label>
ERROR in src/pages/vc/RecruitManagement/detail.tsx:116:24
TS2769: No overload matches this call.
  Overload 1 of 2, '(props: ReactDatePickerProps<undefined, undefined>): ReactDatePicker<undefined, undefined>', gave the following error.
    Property 'onChange' is missing in type '{}' but required in type 'Readonly<ReactDatePickerProps<undefined, undefined>>'.
  Overload 2 of 2, '(props: ReactDatePickerProps<undefined, undefined>, context: any): ReactDatePicker<undefined, undefined>', gave the following error.
    Property 'onChange' is missing in type '{}' but required in type 'Readonly<ReactDatePickerProps<undefined, undefined>>'.
    114 |                     <label className="hide">달력끝</label>
    115 |                     <div className="date-box">
  > 116 |                       <ReactDatePicker />
        |                        ==^====^====^==
    117 |                     </div>
    118 |                   </div>
    119 |                 </li>
ERROR in src/pages/vc/RecruitManagement/detail.tsx:216:24
TS2769: No overload matches this call.
  Overload 1 of 2, '(props: ReactDatePickerProps<undefined, undefined>): ReactDatePicker<undefined, undefined>', gave the following error.
    Property 'onChange' is missing in type '{}' but required in type 'Readonly<ReactDatePickerProps<undefined, undefined>>'.
  Overload 2 of 2, '(props: ReactDatePickerProps<undefined, undefined>, context: any): ReactDatePicker<undefined, undefined>', gave the following error.
    Property 'onChange' is missing in type '{}' but required in type 'Readonly<ReactDatePickerProps<undefined, undefined>>'.
    214 |                     <label className="hide">달력시작</label>
    215 |                     <div className="date-box">
  > 216 |                       <ReactDatePicker />
        |                        ==^====^====^==
    217 |                     </div>
    218 |                     <span> ~ </span>
    219 |                     <label className="hide">달력끝</label>
ERROR in src/pages/vc/RecruitManagement/detail.tsx:221:24
TS2769: No overload matches this call.
  Overload 1 of 2, '(props: ReactDatePickerProps<undefined, undefined>): ReactDatePicker<undefined, undefined>', gave the following error.
    Property 'onChange' is missing in type '{}' but required in type 'Readonly<ReactDatePickerProps<undefined, undefined>>'.
  Overload 2 of 2, '(props: ReactDatePickerProps<undefined, undefined>, context: any): ReactDatePicker<undefined, undefined>', gave the following error.
    Property 'onChange' is missing in type '{}' but required in type 'Readonly<ReactDatePickerProps<undefined, undefined>>'.
    219 |                     <label className="hide">달력끝</label>
    220 |                     <div className="date-box">
  > 221 |                       <ReactDatePicker />
        |                        ==^====^====^==
    222 |                     </div>
    223 |                   </div>
    224 |                 </li>
ERROR in src/pages/vc/smartContract/index.tsx:51:21
TS2345: Argument of type 'gridDataResult<IfTbInsttMaster>' is not assignable to parameter of type 'SetStateAction<gridDataResult<IfTbCmmntyMastr> | undefined>'.
  Type 'gridDataResult<IfTbInsttMaster>' is not assignable to type 'gridDataResult<IfTbCmmntyMastr>'.
    Type 'IfTbInsttMaster' has no properties in common with type 'IfTbCmmntyMastr'.
    49 |     setSelectId('');
    50 |     fnReadList(gridRequest).then((response) => {
  > 51 |       setGridResult(response);
       |                     ==^==^^^
    52 |     });
    53 |   };
    54 |   return (```
    * 원인
      * The errors related to 'ReactDatePicker' are indicating that 'onChange' property is required but not provided. 
      * The suggests that the type 'gridDataResult<IfTbInstMastr>' is not assignable to 'gridDataResult<IfTbCmmntyMastr>', that is type mismatch. 
    * 조치 1
      * ```javascript
// 바우처 모집대상 목록 - 상세
export default function CommunityNoticeManagementDetail({ listViewRef, selectId, closeDetail }: DetailProps) {
  const { fnReadDetail, fnReadList, filterItems, headerList } = useActionHook();
  const [detail, setDetail] = useState<IfTbCmmntyMastr>({} as IfTbCmmntyMastr); // <-- Modified initial state to match interface
  const [totalCnt, setTotalCnt] = useState(0);
  const [startDate, setStartDate] = useState<Date | null>(null); // <-- Added state for start date
  const [endDate, setEndDate] = useState<Date | null>(null); // <-- Added state for end date
...
  
                  <div className="date-box">
                      <ReactDatePicker
                        selected={startDate} // <-- Added selected prop
                        onChange={(date: Date | null) => setStartDate(date)} // <-- Added onChange prop
                        dateFormat="yyyy/MM/dd" // <-- Added date format
                      />
                    </div>```
    * 조치 2
      * ```javascript
smartContract는 스마트계약 타입을 써야 하는데 IfTbCmmntyMastr 타입을 써서 발생한 에러.

import { IfPageView, IfTbCmmntyMastr } from '@services/types';
--> import { IfPageView, IfTbSmartContractMastr } from '@services/types';
...
// 그리드로우선택
  const fnRowAction = (row: IfTbSmartContractMastr) => {
    if (detailView === 'create') {
      openToast({ color: 'red', content: '기관정보 등록을 완료해주세요.' });
      return;
    }
    setSelectId(row.nttManageId!); --> setSelectId(row.coinId!); 로 수정!
    setDetailView('detail');
    setTimeout(() => {
      listViewRef && listViewRef.current && listViewRef.current.scrollIntoView({ behavior: 'smooth' });
    });
  };

```
  * 08:45 3개비
  * 08:52 문찬원 과장에게 화면 에러 설명
  * 개발 계획
    * [[Roam/genext-2025-10-05-02-18-30/August 8th, 2024#^V_KbN7f5x|17:06 바우처 모집대상 관련 개발 시작.]]
  * 12:11 모집대상 목록을 뽑기 위한 sql 작성
    * ```sql
select 
  ...
  ic.induty_nm,
  -- i.instt_nm, 한 바우처에 업종 코드가 하나만 등록되는 경우는 거의 없으므로 이 줄은 별 의미가 없고 다음 줄이 현실적.
  GROUP_CONCAT(DISTINCT IC.INDUTY_NM ORDER BY IC.INDUTY_NM SEPARATOR ', ') AS INDUTY_NM,
  (select count(*) from tb_vouch_place where vouch_id = vm.vouch_id) as place_count,
  sum(
    case 
      when cr.reqst_yn = 'Y' then 1
      else 0
    end) as reqst_y_count,
  sum(
    case
      when cr.reqst_yn = 'N' then 1
      else 0
    end) as reqst_n_count,
  count(cr.reqst_yn) as total_reqst_count
  from tb_vouch_mastr vm
  left join tb_cstmr_rcrit cr on cr.vouch_id = vm.vouch_id
  left join tb_vouch_induty vi on vi.vouch_id = vm.vouch_id
  left join tb_induty_cd ic on ic.induty_cd = vi.induty_cd
  left join tb_instt i on i.prt_cmpny_id = vm.prt_cmpny_id
  where 1 = 1
    and vm.prt_cmpny_id = 의뢰기관 ID
    and vm.vouch_id = "상세조회 시 쓰는 voucher ID"
  ```
  * 14:57 sql 작성 후 전반적인 구조 작성
  * 16:40 바우처 모집 정보 조회 테스트 에러 발생
    * 에러
      * ```plain text
Invalid bound statement (not found): kr.or.cbdc.domain.main.mapper.voucher.recruit.TbVcRecruitMapper.selectRecruitInfo
org.apache.ibatis.binding.BindingException: Invalid bound statement (not found): kr.or.cbdc.domain.main.mapper.voucher.recruit.TbVcRecruitMapper.selectRecruitInfo```
    * 원인
      * sql.xml에서 참조할 mapper interface 파일명이 잘못됨
  * 16:50 조회는 정상적으로 되었지만 숫자가 나와야 하는 부분이 null.
    * 원인: 변수 타입을 Integer로 하지 않고 Int로 한 것이 원인.
      * ```java
package kr.or.cbdc.domain.main.model.voucher.recruit.mastr;

import kr.or.cbdc.domain.main.model.MainEntity;
import kr.or.cbdc.infrastructure.idgen.util.IdGenerationUtil;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.SuperBuilder;
import org.web3j.abi.datatypes.Int;

@Getter
@Setter
@SuperBuilder
@NoArgsConstructor
public class TbVcRecruit extends MainEntity {

    private static final long serialVersionUID = -5767295897536796925L;

    protected String vouchId;
    protected String prtCmpnyId;
    protected String vouchNm;
    protected String vouchRcritStartDt;
    protected String vouchRcritEndDt;
    protected String vouchTotamt;
    protected String vouchBankCode;
    protected String userWhlrs;
    protected String insttNm;
    protected String indutyNm; // 여러 개 있을 경우 "A, B, C"로 표시된다.
    protected Int placeCount;
    protected Int reqstYCount;
    protected Int reqstNCount;
    protected Int totalReqstCount;

    /*
    public TbVcRecruit newId() {
        this.setCstmrNo(IdGenerationUtil.createUid("TB_CSTMR_RCRIT"));

        return this;
    }
     */

}
```
    * 조치: 자바에서는 wrapper 클래스인 Integer를 써야 함.
  * 17:12 바우처 모집 정보 중 신청자 목록 조회 시작
