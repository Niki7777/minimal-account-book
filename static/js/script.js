// 全局基础配置
const API_BASE = 'http://localhost:3000/api';

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 1. 首页：新增消费项表单提交
    const consumptionForm = document.getElementById('consumptionForm');
    if (consumptionForm) {
        consumptionForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = {
                content: document.getElementById('content').value,
                quantity: document.getElementById('quantity').value,
                totalPrice: document.getElementById('totalPrice').value,
                channel: document.getElementById('channel').value,
                mainType: document.getElementById('mainType').value,
                subType: document.getElementById('subType').value,
                unitCoefficient: document.getElementById('unitCoefficient').value,
                receiveStatus: document.getElementById('receiveStatus').value
            };

            try {
                const response = await fetch(`${API_BASE}/consumption`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                const result = await response.json();
                if (result.success) {
                    alert('消费项添加成功！');
                    consumptionForm.reset(); // 重置表单
                } else {
                    alert(`添加失败：${result.message}`);
                }
            } catch (error) {
                alert('网络错误，添加失败！');
                console.error(error);
            }
        });
    }

    // 2. 通用：删除消费项
    const deleteBtns = document.querySelectorAll('.delete-btn');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', async function() {
            const id = this.getAttribute('data-id');
            if (!confirm(`确认删除ID为${id}的消费项吗？`)) return;

            try {
                const response = await fetch(`${API_BASE}/consumption/${id}`, {
                    method: 'DELETE'
                });
                const result = await response.json();
                if (result.success) {
                    alert('删除成功！');
                    window.location.reload(); // 刷新页面
                } else {
                    alert(`删除失败：${result.message}`);
                }
            } catch (error) {
                alert('网络错误，删除失败！');
                console.error(error);
            }
        });
    });

    // 3. 消费列表：修改打标
    const tagSelects = document.querySelectorAll('.tag-select');
    tagSelects.forEach(select => {
        select.addEventListener('change', async function() {
            const id = this.getAttribute('data-id');
            const tag = this.value;

            try {
                const response = await fetch(`${API_BASE}/consumption/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tag })
                });
                const result = await response.json();
                if (!result.success) {
                    alert(`修改打标失败：${result.message}`);
                }
            } catch (error) {
                alert('网络错误，修改失败！');
                console.error(error);
            }
        });
    });

    // 4. 消费列表：设置日均价弹窗
    const editDailyPriceBtns = document.querySelectorAll('.edit-daily-price');
    const dailyPriceModal = document.getElementById('dailyPriceModal');
    const closeModalBtn = document.getElementById('closeModal');
    const saveDailyPriceBtn = document.getElementById('saveDailyPrice');
    let currentConsumptionId = '';

    if (editDailyPriceBtns.length && dailyPriceModal) {
        editDailyPriceBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                currentConsumptionId = this.getAttribute('data-id');
                document.getElementById('modalId').value = currentConsumptionId;
                document.getElementById('modalTotalPrice').value = this.getAttribute('data-total-price');
                dailyPriceModal.style.display = 'flex';
            });
        });

        // 关闭弹窗
        closeModalBtn.addEventListener('click', function() {
            dailyPriceModal.style.display = 'none';
        });

        // 点击弹窗外层关闭
        dailyPriceModal.addEventListener('click', function(e) {
            if (e.target === dailyPriceModal) {
                dailyPriceModal.style.display = 'none';
            }
        });

        // 保存日均价
        saveDailyPriceBtn.addEventListener('click', async function() {
            const startUseTime = document.getElementById('startUseTime').value;
            const endUseTime = document.getElementById('endUseTime').value;
            if (!startUseTime || !endUseTime) {
                alert('开始/结束使用时间不能为空！');
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/consumption/${currentConsumptionId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        startUseTime,
                        endUseTime
                    })
                });
                const result = await response.json();
                if (result.success) {
                    alert('日均价设置成功！');
                    dailyPriceModal.style.display = 'none';
                    window.location.reload();
                } else {
                    alert(`设置失败：${result.message}`);
                }
            } catch (error) {
                alert('网络错误，设置失败！');
                console.error(error);
            }
        });
    }

    // 5. 待收货列表：确认收货
    const confirmReceiveBtns = document.querySelectorAll('.confirm-receive');
    confirmReceiveBtns.forEach(btn => {
        btn.addEventListener('click', async function() {
            const id = this.getAttribute('data-id');
            if (!confirm('确认收货吗？收货后会计入账单统计！')) return;

            try {
                const response = await fetch(`${API_BASE}/consumption/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ receiveStatus: '已收货' })
                });
                const result = await response.json();
                if (result.success) {
                    alert('确认收货成功！');
                    window.location.reload();
                } else {
                    alert(`确认失败：${result.message}`);
                }
            } catch (error) {
                alert('网络错误，确认失败！');
                console.error(error);
            }
        });
    });

    // 6. 价格查询：查询历史价格
    const queryPriceBtn = document.getElementById('queryPriceBtn');
    if (queryPriceBtn) {
        queryPriceBtn.addEventListener('click', async function() {
            const subType = document.getElementById('subTypeSelect').value;
            if (!subType) {
                alert('请选择细分类型！');
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/consumption/type/${subType}`);
                const result = await response.json();
                const priceTable = document.getElementById('priceTable');
                const priceTableBody = document.getElementById('priceTableBody');
                const priceEmptyTip = document.getElementById('priceEmptyTip');

                if (result.success && result.data.length) {
                    priceTableBody.innerHTML = '';
                    result.data.forEach(item => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>${item.create_time}</td>
                            <td>${item.content}</td>
                            <td>${item.quantity}</td>
                            <td>${item.total_price}</td>
                            <td>${item.min_unit_price}</td>
                            <td>${item.tag || '无'}</td>
                        `;
                        priceTableBody.appendChild(tr);
                    });
                    priceTable.style.display = 'table';
                    priceEmptyTip.style.display = 'none';
                } else {
                    priceTable.style.display = 'none';
                    priceEmptyTip.textContent = '暂无该类型的历史价格数据～';
                    priceEmptyTip.style.display = 'block';
                }
            } catch (error) {
                alert('网络错误，查询失败！');
                console.error(error);
            }
        });
    }

    // 7. 通用：更新待收货数量（防止缓存）
    fetch(`${API_BASE}/consumption/pending`)
        .then(res => res.json())
        .then(result => {
            const pendingCountEls = document.querySelectorAll('#pendingCount');
            pendingCountEls.forEach(el => {
                el.textContent = result.count || 0;
            });
        })
        .catch(err => console.error('更新待收货数量失败：', err));
});