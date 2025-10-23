---
title: "November 22nd, 2023"
created: 2023-11-22 06:50:42
updated: 2023-11-23 09:17:09
---
  * [x] Less than two months ago, on stage at the Code Conference, I asked Helen Toner how she thought about the awesome power that she’d been entrusted with as a board member at OpenAI. Toner has the power under the company’s charter to halt OpenAI’s efforts to build an artificial general intelligence. If the circumstances presented themselves, would she really stop the company’s work and redirect employees to working on other projects?

At the time, Toner demurred. I had worded my question inelegantly, suggesting that she might be able to shut down the company entirely. The moment passed, and I never got my answer — until this weekend, when the board Toner serves on effectively ended OpenAI as we know it. (She declined to comment when I emailed her.)
  * 13:29 admin 메뉴의 프롬프트 관리 들어가는 방법
    * http://localhost:3000/admin/prompt
  * 14:17 현재 보고서 생성 시 prompttemplate을 사용한다. 나중에 프롬프트 설정 개발이 완료되면 이것이 prompttemplate을 대신해야 한다?
  * 15:04 promptData를 API 호출해서 얻기.
    * ```javascript
import { useState, useEffect } from 'react';
import axiosUtil from '@/path/to/axiosUtil'; // Update with the correct path

export default function AdminPromptDetail() {
  const [promptTypeData, setPromptTypeData] = useState([]);
  const [mtypeValue, setMtypeValue] = useState('');

  useEffect(() => {
    const fetchPromptTypeData = async () => {
      try {
        const response = await axiosUtil.get('/api/path/to/promptTypeData'); // Update with the correct API endpoint
        const transformedData = response.data.map(item => ({
          id: item._id,
          label: item.type,
          isChecked: false
        }));
        setPromptTypeData(transformedData);
      } catch (error) {
        console.error('Error fetching prompt type data:', error);
        // Handle error appropriately
      }
    };

    fetchPromptTypeData();
  }, []);

  // Rest of your component logic...

  return (
    // Your JSX code...
    <li>
      <h3 className="required">모듈 유형</h3>
      <div className="wrap-select">
        <select value={mtypeValue} onChange={(e) => setMtypeValue(e.target.value)}>
          <option value="">{mtypeValue}</option>
          {promptTypeData.map((option) => (
            <option key={option.id} value={option.id}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
    </li>
    // Other parts of your JSX...
  );
}
```