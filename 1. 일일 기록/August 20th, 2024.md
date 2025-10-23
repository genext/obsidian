---
title: "August 20th, 2024"
created: 2024-08-20 06:49:11
updated: 2024-10-24 10:34:53
---
  * 06:45 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 엑셀 upload 받은 것 DB에 저장(수혜자, 사용처)

  * 명경지수
  * 08:13 사용자 권한 별 화면 변경 여부 확인 위해 user9을 일반 사용자로 권한 설정하려고 함.
    * 만일을 위해 TB_SYS_USER_AUTHOR 먼저 export해서 데이터 저장.
    * ![[100. media/documents/oZspaDVDtM.csv]]
  * 08:15 모집관리 화면에 의뢰기관으로 로그인할 때와 참가기관으로 로그인할 때 화면 구성 변경 확인 테스트 시작
    * TB_SYS_USER_AUTHOR에서 user9의 권한을 ROLE_USER만 남기고 다 삭제.
  * 08:21 권한에 따른 화면 변경(수혜자, 사용처 업로드 버튼 동적 표시) 확인 OK.
  * 09:01 수호 아이오 이정주 팀장이 DB에 audit log 남기는 것을 막고 싶다고 했다.
    * 일단 로그는 interceptor가 관련되어 있을 거라는 생각이 들었다. 검색 결과 정리
      * 검색어 위주로 검색 시작
        * TB_SYS_UID -> application.log -> TbSysLog -> LoggingMyBatisInterceptor가 StatementLogInterceptor를 상속하는 것을 발견
      * 방법 세 가지
        * myBatis config를 바꿔서 해당 인터셉터 자체가 뜨지 못하게 하는 것
        * application.yml에 "app.logging.interceptor.enabled=false" 같은 것을 추가해서 인터셉터 클래스에서 해당 변수를 읽어서 로그 안 찍게 하는 방법
        * [x] 하지만 현 프로젝트에서는 MDC (Mapped Diagnostic Context)를 쓴다. MDC 파악
      * 마지막 방법을 선택해서 "MDC.put("log.jdbc.disabled", "1");"를 소스에 추가.
        * ```java
package kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.interceptor;

import java.lang.reflect.InvocationTargetException;
import java.util.List;
import java.util.Properties;

import org.apache.commons.lang3.StringUtils;
import org.apache.ibatis.executor.statement.StatementHandler;
import org.apache.ibatis.mapping.BoundSql;
import org.apache.ibatis.mapping.MappedStatement;
import org.apache.ibatis.mapping.ParameterMapping;
import org.apache.ibatis.plugin.Interceptor;
import org.apache.ibatis.plugin.Invocation;
import org.apache.ibatis.plugin.Plugin;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public abstract class StatementLogInterceptor implements Interceptor {

    private static final Logger log = LoggerFactory.getLogger(StatementLogInterceptor.class);

    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        // Disable logging by setting the MDC context
        MDC.put("log.jdbc.disabled", "1");        <------------------------- 추가
        StatementHandler handler = (StatementHandler) invocation.getTarget();
        BoundSql boundSql = handler.getBoundSql();
        String sql = boundSql.getSql();
        List<ParameterMapping> parameterMappingList = boundSql.getParameterMappings();
        StringBuilder parameter = new StringBuilder();

        if (parameterMappingList.size() > 0) {
            for (ParameterMapping parameterMapping : parameterMappingList) {
                parameter.append(parameterMapping.toString() + "\n");
            }
            Object parameterObject = boundSql.getParameterObject();
            parameter.append(StringUtils.leftPad("", 80, "-") + "\n");
            parameter.append(parameterObject.toString());
        }

        try {
            return invocation.proceed();
        } catch (InvocationTargetException e) {
            throw e;
        } catch (IllegalAccessException e) {
            throw e;
        } catch (RuntimeException e) {
            throw e;
        } finally {
            if (!StringUtils.equals(MDC.get("log.jdbc.disabled"), "1")) {
                String id = MDC.get(MappedStatement.class.getName() + ".id");

                try {
                    MDC.put("log.jdbc.disabled", "1");

                    this.createLog(id, sql, parameter.toString());
                } catch (RuntimeException e) {
                    log.error(e.getMessage(), e);
                } finally {
                    MDC.remove("log.jdbc.disabled");
                }
            }
        }
    }

    @Override
    public Object plugin(Object target) {
        return Plugin.wrap(target, this);
    }

    @Override
    public void setProperties(Properties properties) {
    }

    public abstract void createLog(String id, String sql, String parameter);

}
```
  * 11:09 swagger에서는 token을 등록하고 하기 때문에 파일 업로드가 되었다. 하지만 front-end에서 내가 직접 axios로 요청을 보낼 때 token을 붙이지 않았다.
  * 11:34 수혜자 엑셀 전송 테스트 완료. 이번에 애먹은 이유는 token 전송해야 한다는 것을 잊었기 때문.
  * [ ] getApi, postApi와 예전 sk c&c에서 사용한 axio util 비교 정리.
    * ```javascript
import useAxios from '@services/api/axiosApi';
import useBankModal from '@component/modal/modalHook';
import saveAs from 'file-saver';
interface ApiOptions {
  url: string;
  accessTokenFlag?: boolean;
  isLoading?: boolean;
  isError?: boolean;
  isOtp?: boolean;
  eMessage?: string;
  sMessage?: string;
  contentType?: string;
  config?: any;
  isHeader?: boolean;
}
//공통API
export default function useCommonApi() {
  const { createInstance } = useAxios();
  const { openToast, closeLoading, openLoading, openOtp } = useBankModal();

  const getApi = async <V>(options: ApiOptions): Promise<V | null> => {
    if (options.isOtp && (await openOtp()) === false) return null;

    const key = options.isLoading !== false ? openLoading() : '';

    try {
      const { data } = await createInstance({
        accessTokenFlag: options.accessTokenFlag !== false,
        contentType: options.contentType
      }).get<V>(options.url, options.config);
      options.sMessage && openToast({ color: 'app', content: options.sMessage });
      return data;
    } catch (error: any) {
      if (error.status === 99999) {
        openToast({ color: 'app', content: error.message, only: true });
      } else {
        options.isError !== false && openToast({ color: 'red', content: options.eMessage ?? error?.message });
      }
      return null;
    } finally {
      options.isLoading !== false && closeLoading(key);
    }
  };

  const postApi = async <T, V>(options: ApiOptions, params?: T): Promise<V | null> => {
    if (options.isOtp && (await openOtp()) === false) return null;
    const key = options.isLoading !== false ? openLoading() : '';
    try {
      const { data } = await createInstance({
        accessTokenFlag: options.accessTokenFlag !== false,
        contentType: options.contentType
      }).post<V>(options.url, params, {
        headers: { 'Content-Type': options.contentType ?? 'application/json;charset=UTF-8' }
      });
      options.sMessage && openToast({ color: 'app', content: options.sMessage });
      return data;
    } catch (error: any) {
      if (options.url === 'users/login' || options.url === '/users/login') {
        let content = '로그인 시도 중 오류가 발생했습니다.';
        if (error && error.status) {
          switch (error.status) {
            case 400:
              content = '서버 호출 중 오류가 발생했습니다.';
              break;
            case 403:
              content = '허가되지 않은 IP입니다.';
              break;
            case 401:
              content = 'ID/비밀번호가 일치하지 않습니다.';
              break;
            default:
              content = error.message;
          }
        }
        openToast({ content: content, color: 'red' });
      } else {
        if (error.status === 99999) {
          openToast({ color: 'app', content: error.message, only: true });
        } else {
          options.isError !== false && openToast({ color: 'red', content: options.eMessage ?? error?.message });
        }
      }
      return null;
    } finally {
      options.isLoading !== false && closeLoading(key);
    }
  };
  const postHeaderApi = async <T, V>(options: ApiOptions, params?: T): Promise<any> => {
    if (options.isOtp && (await openOtp()) === false) return null;

    const key = options.isLoading !== false ? openLoading() : '';
    try {
      const response = await createInstance({
        accessTokenFlag: options.accessTokenFlag !== false,
        contentType: options.contentType
      }).post<V>(options.url, params, {
        headers: { 'Content-Type': options.contentType ?? 'application/json;charset=UTF-8' }
      });
      options.sMessage && openToast({ color: 'app', content: options.sMessage });
      return response;
    } catch (error: any) {
      if (options.url === 'users/login' || options.url === '/users/login') {
        let content = '로그인 시도 중 오류가 발생했습니다.';
        if (error && error.status) {
          switch (error.status) {
            case 400:
              content = '서버 호출 중 오류가 발생했습니다.';
              break;
            case 403:
              content = '허가되지 않은 IP입니다.';
              break;
            case 401:
              content = 'ID/비밀번호가 일치하지 않습니다.';
              break;
            default:
              content = error.message;
          }
        }
        openToast({ content: content, color: 'red' });
      } else {
        if (error.status === 99999) {
          openToast({ color: 'app', content: error.message, only: true });
        } else {
          options.isError !== false && openToast({ color: 'red', content: options.eMessage ?? error?.message });
        }
      }
      return error;
    } finally {
      options.isLoading !== false && closeLoading(key);
    }
  };
  const postMdifyApi = async <T>(options: ApiOptions, params?: T): Promise<boolean> => {
    if (options.isOtp && (await openOtp()) === false) return false;
    const key = options.isLoading !== false ? openLoading() : '';
    try {
      await createInstance({ accessTokenFlag: options.accessTokenFlag !== false, contentType: options.contentType }).post<any>(options.url, params, {
        headers: { 'Content-Type': options.contentType ?? 'application/json;charset=UTF-8' }
      });
      options.sMessage && openToast({ color: 'app', content: options.sMessage });
      return true;
    } catch (error: any) {
      if (error.status === 99999) {
        openToast({ color: 'app', content: error.message, only: true });
      } else {
        options.isError !== false && openToast({ color: 'red', content: options.eMessage ?? error?.message });
      }
      return false;
    } finally {
      options.isLoading !== false && closeLoading(key);
    }
  };
  const putApi = async <T>(options: ApiOptions, params: T): Promise<boolean> => {
    if (options.isOtp && (await openOtp()) === false) return false;
    const key = options.isLoading !== false ? openLoading() : '';
    try {
      await createInstance({ accessTokenFlag: options.accessTokenFlag !== false }).put<any>(options.url, params);
      options.sMessage && openToast({ color: 'app', content: options.sMessage });
      return true;
    } catch (error: any) {
      if (error.status === 99999) {
        openToast({ color: 'app', content: error.message, only: true });
      } else {
        options.isError !== false && openToast({ color: 'red', content: options.eMessage ?? error?.message });
      }
      return false;
    } finally {
      options.isLoading !== false && closeLoading(key);
    }
  };
  const deleteApi = async (options: ApiOptions): Promise<boolean> => {
    if (options.isOtp && (await openOtp()) === false) return false;
    const key = options.isLoading !== false ? openLoading() : '';
    try {
      await createInstance({ accessTokenFlag: options.accessTokenFlag !== false, contentType: options.contentType }).delete<any>(options.url);
      options.sMessage && openToast({ color: 'app', content: options.sMessage });
      return true;
    } catch (error: any) {
      if (error.status === 99999) {
        openToast({ color: 'app', content: error.message, only: true });
      } else {
        options.isError !== false && openToast({ color: 'red', content: options.eMessage ?? error?.message });
      }
      return false;
    } finally {
      options.isLoading !== false && closeLoading(key);
    }
  };
  const fileDownloadApi = async <T>(options: ApiOptions, fileName: string, type?: 'get' | 'post', params?: T): Promise<boolean> => {
    if (options.isOtp && (await openOtp()) === false) return false;
    const key = options.isLoading !== false ? openLoading() : '';
    try {
      let response;
      if (type === 'get') {
        response = await createInstance({
          accessTokenFlag: options.accessTokenFlag !== false,
          contentType: options.contentType
        }).get<Blob>(options.url, {
          responseType: 'blob'
        });
      } else {
        response = await createInstance({
          accessTokenFlag: options.accessTokenFlag !== false,
          contentType: options.contentType
        }).post<Blob>(options.url, params, {
          responseType: 'blob'
        });
      }
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      saveAs(blob, fileName);
      if (options.sMessage) openToast({ color: 'app', content: options.sMessage });
      return true;
    } catch (error: any) {
      if (error.status === 99999) {
        openToast({ color: 'app', content: error.message, only: true });
        return false;
      }

      if (options.isError !== false) openToast({ color: 'red', content: options.eMessage ?? error.message });
      return false;
    } finally {
      if (options.isLoading !== false) closeLoading(key);
    }
  };
  return {
    getApi,
    postApi,
    postHeaderApi,
    postMdifyApi,
    putApi,
    deleteApi,
    fileDownloadApi
  };
}
```