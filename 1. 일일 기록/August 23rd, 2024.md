---
title: "August 23rd, 2024"
created: 2024-08-23 06:05:11
updated: 2024-10-23 16:21:50
---
  * 06:01 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 모집관리 조회 갑자기 상세 조회가 안 되는 이유 찾기

  * 명경지수
  * 06:57 지금 모집관리 신청자 조회가 안 되는 원인 찾는 중.
    * 서버쪽은 정상 쿼리해서 3건 던져주지만 브라우저 디버그 창에서는 아예 response를 안 받은 것으로 나옴. 뭐지?
    * 신청처리 수도 제대로 안 나온다. 일부는 나오고 일부는 안 나온다. 
    * 일단 참가기관용 화면을 먼저 하자. 여기서 실마리가 풀릴지 모른다.
  * [x] 11:22 숫자가 안 나오는 이유를 찾았다. AI 도움으로.
    * return 안에 {/* {(props.value || props.inputMode) && fnRow()} */} 이게 문제였다. 
    * ```javascript
import { CSSProperties, HTMLInputAutoCompleteAttribute, ReactNode } from 'react';
import TextUtil from '@component/util/textUtil';
import NumberInput from '@component/input/numberInput';
import TextInput from '@component/input/textInput';
import TextAreaInput from '@component/input/textAreaInput';
import RadioInput from '@component/input/radioInput';
import SelectInput from '@component/input/selectInput';
import CheckboxInput from '@component/input/checkboxInput';
import PasswordInput from '@component/input/passwordInput';
import FileInput from '@component/input/fileInput';
import AddrInput from '@component/input/addrInput';
import ReactDatePicker from '@component/input/inputDate';
import { IfComCode } from '@services/types';
interface InputBastProps {
  className?: string;
  style?: CSSProperties;
  isError?: boolean;
  disabled?: boolean;
}
interface TextOptionsProps extends InputBastProps {
  placeholder?: string;
  maxLength?: number;
  onChange?: (value: string) => void;
}
interface TextareaOptionsProps extends InputBastProps {
  placeholder?: string;
  maxLength?: number;
  onChange?: (value: string) => void;
}
interface NumberOptionsProps extends InputBastProps {
  placeholder?: string;
  maxLength?: number;
  isShot?: boolean;
  isCurrency?: boolean;
  onChange?: (value: string) => void;
}
interface RadioOptionsProps extends InputBastProps {
  options: Array<IfComCode>;
  onChange?: (value: string) => void;
}
interface SelectOptionsProps extends InputBastProps {
  options: Array<IfComCode>;
  onChange?: (value: string) => void;
}
interface CheckboxOptionsProps {
  className?: string;
  style?: CSSProperties;
  isError?: boolean;
  options: Array<any>;
  name: string;
  checked: string;
  onChange: (value: EventTarget & HTMLInputElement) => void;
  disabled?: string | boolean;
}
interface PasswordOptionsProps extends InputBastProps {
  placeholder?: string;
  maxLength?: number;
  autoComplete?: HTMLInputAutoCompleteAttribute;
  onChange?: (value: string) => void;
}
interface FileOptionsProps {
  fileExts: Array<'xlsx' | 'xls' | 'txt' | 'csv' | 'zip' | 'abi' | 'bin'>;
  fileMaxSize?: number;
  spanText?: string;
  onChange: (value: File | null, data?: Array<any>) => void;
  className?: string;
  disabled?: boolean;
  errMessage?: string;
}
interface DatePickerProps {
  setValue: (date: Date | null) => void;
  minDate?: Date | null;
  maxDate?: Date | null;
}
// row
interface RowProps {
  isReq?: boolean;
  label?: string;
  value?: string | number | Date | Array<number> | null | undefined;
  valueType?: 'datetime' | 'date' | 'date2' | 'amount' | 'phone';
  colSpan?: number;
  isNotTh?: boolean;
  thClassName?: string;
  tdClassName?: string;
  spanClassName?: string;
  thStyle?: CSSProperties;
  tdStyle?: CSSProperties;
  onSpanClick?: () => void;
  inputMode?: 'text' | 'number' | 'radio' | 'select' | 'checkbox' | 'textarea' | 'password' | 'file' | 'addr' | 'date' | '' | null | undefined;
  textOptions?: TextOptionsProps;
  textareaOptions?: TextareaOptionsProps;
  numberOptions?: NumberOptionsProps;
  radioOptions?: RadioOptionsProps;
  selectOptions?: SelectOptionsProps;
  checkboxOptions?: CheckboxOptionsProps;
  passwordOptions?: PasswordOptionsProps;
  fileOptions?: FileOptionsProps;
  dateOptions?: DatePickerProps;
  children?: ReactNode;
}

export default function Row(props: RowProps) {
  const fnRow = () => {
    if (props.inputMode) {
      if (props.inputMode === 'text' && props.textOptions) {
        return (
          <TextInput
            value={props.value as string | null | undefined}
            label={props.label}
            placeholder={props.textOptions.placeholder}
            className={props.textOptions.className}
            style={props.textOptions.style}
            isError={props.textOptions.isError}
            maxLength={props.textOptions.maxLength}
            onChange={props.textOptions.onChange!}
            disabled={props.textOptions.disabled}
          />
        );
      } else if (props.inputMode === 'number' && props.numberOptions) {
        return (
          <NumberInput
            value={props.value as string | number | null | undefined}
            label={props.label}
            placeholder={props.numberOptions.placeholder}
            className={props.numberOptions.className}
            style={props.numberOptions.style}
            isShot={props.numberOptions.isShot}
            isCurrency={props.numberOptions.isCurrency}
            isError={props.numberOptions.isError}
            maxLength={props.numberOptions.maxLength}
            onChange={props.numberOptions.onChange!}
            disabled={props.numberOptions.disabled}
          />
        );
      } else if (props.inputMode === 'textarea' && props.textareaOptions) {
        return (
          <TextAreaInput
            value={props.value as string | null | undefined}
            label={props.label}
            placeholder={props.textareaOptions.placeholder}
            className={props.textareaOptions.className}
            style={props.textareaOptions.style}
            isError={props.textareaOptions.isError}
            maxLength={props.textareaOptions.maxLength}
            onChange={props.textareaOptions.onChange!}
            disabled={props.textareaOptions.disabled}
          />
        );
      } else if (props.inputMode === 'radio' && props.radioOptions) {
        return (
          <RadioInput
            value={props.value as string | null | undefined}
            label={props.label}
            options={props.radioOptions.options}
            className={props.radioOptions.className}
            style={props.radioOptions.style}
            isError={props.radioOptions.isError}
            onChange={props.radioOptions.onChange!}
            disabled={props.radioOptions.disabled}
          />
        );
      } else if (props.inputMode === 'select' && props.selectOptions) {
        return (
          <SelectInput
            value={props.value as string | null | undefined}
            label={props.label}
            options={props.selectOptions.options}
            className={props.selectOptions.className}
            style={props.selectOptions.style}
            isError={props.selectOptions.isError}
            onChange={props.selectOptions.onChange!}
            disabled={props.selectOptions.disabled}
          />
        );
      } else if (props.inputMode === 'checkbox' && props.checkboxOptions) {
        return (
          <CheckboxInput
            value={props.value as string}
            options={props.checkboxOptions.options}
            className={props.checkboxOptions.className}
            style={props.checkboxOptions.style}
            isError={props.checkboxOptions.isError}
            name={props.checkboxOptions.name}
            checked={props.checkboxOptions.checked}
            onChange={props.checkboxOptions.onChange}
            disabled={props.checkboxOptions.disabled}
          />
        );
      } else if (props.inputMode === 'password' && props.passwordOptions) {
        return (
          <PasswordInput
            value={props.value as string | null | undefined}
            label={props.label}
            placeholder={props.passwordOptions.placeholder}
            maxLength={props.passwordOptions.maxLength}
            autoComplete={props.passwordOptions.autoComplete}
            className={props.passwordOptions.className}
            style={props.passwordOptions.style}
            isError={props.passwordOptions.isError}
            onChange={props.passwordOptions.onChange!}
            disabled={props.passwordOptions.disabled}
          />
        );
      } else if (props.inputMode === 'file' && props.fileOptions) {
        return (
          <FileInput
            fileExts={props.fileOptions.fileExts!}
            fileMaxSize={props.fileOptions.fileMaxSize}
            className={props.fileOptions.className}
            onChange={props.fileOptions.onChange!}
            spanText={props.fileOptions.spanText}
            disabled={props.fileOptions.disabled}
            errMessage={props.fileOptions.errMessage}
          />
        );
      } else if (props.inputMode === 'addr') {
        return props.value && <AddrInput value={props.value as string | null | undefined} />;
      } else if (props.inputMode === 'date' && props.dateOptions) {
        return (
          <div className="ipt-flex">
            <label className="hide">달력시작</label>
            <div className="date-box">
              <ReactDatePicker
                value={props.value as Date | null}
                setValue={props.dateOptions.setValue}
                maxDate={props.dateOptions.maxDate}
                minDate={props.dateOptions.minDate}
              />
            </div>
          </div>
        );
      }
    }
    if (props.valueType === 'amount') {
      return <span className={'amount'}>{TextUtil.rowParsevalue(props.value, props.valueType)}</span>;
    } else if (props.spanClassName) {
      return (
        <span className={props.spanClassName} onClick={() => props?.onSpanClick && props.onSpanClick()}>
          {TextUtil.rowParsevalue(props.value, props.valueType)}
        </span>
      );
    } else {
      return TextUtil.rowParsevalue(props.value, props.valueType);
    }
  };
  return (
    <>
      {!props.isNotTh && (
        <th
          className={`${props.isReq ? 'req' : props.inputMode && props.isReq !== false && props.inputMode !== 'addr' ? 'req' : ''} ${props.thClassName ?? ''}`}
          style={props.thStyle ? props.thStyle : {}}
        >
          {props.label}
        </th>
      )}
      <td
        className={`${props.valueType === 'amount' ? 'text-end' : ''} ${props.tdClassName ?? ''}`}
        colSpan={props.colSpan ?? 1}
        style={props.tdStyle ? props.tdStyle : {}}
      >
        {/* {(props.value || props.inputMode) && fnRow()} */}
        {(props.value !== null && props.value !== undefined) || props.inputMode ? fnRow() : null}
        {props?.children}
      </td>
    </>
  );
}
```
  * 이제 Applcnt가 안 나오는 것만 해결하면 된다.
  * [x] web 3.0 이해. 시맨틱웹과 무슨 관계?
