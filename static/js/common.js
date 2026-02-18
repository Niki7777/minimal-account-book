// 公共JavaScript函数

/**
 * 显示Toast提示
 * @param {string} message - 提示消息
 * @param {string} type - 提示类型 ('info', 'success', 'error')
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const msg = document.getElementById('toastMessage');
    const icon = document.getElementById('toastIcon');
    
    msg.textContent = message;
    
    // 设置图标和颜色
    if (type === 'error') {
        icon.className = 'fas fa-times-circle text-red-400';
    } else if (type === 'success') {
        icon.className = 'fas fa-check-circle text-green-400';
    } else {
        icon.className = 'fas fa-info-circle text-blue-400';
    }
    
    toast.classList.remove('hidden');
    
    // 3秒后自动隐藏
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

/**
 * 确认对话框（移动端友好）
 * @param {string} message - 确认消息
 * @returns {Promise<boolean>} 用户选择的结果
 */
function showConfirm(message) {
    return new Promise((resolve) => {
        // 检查是否在移动端
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            // 移动端使用自定义确认弹窗
            const confirmModal = document.createElement('div');
            confirmModal.className = 'fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4';
            confirmModal.id = 'mobileConfirmModal';
            
            confirmModal.innerHTML = `
                <div class="bg-white rounded-xl w-full max-w-md p-6">
                    <div class="text-center">
                        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
                            <i class="fa fa-question text-blue-600 text-xl"></i>
                        </div>
                        <h3 class="mt-4 text-lg font-medium text-gray-800">确认操作</h3>
                        <p class="mt-2 text-gray-600">${message}</p>
                        <div class="mt-6 flex flex-col sm:flex-row sm:justify-center gap-3">
                            <button id="confirmCancel" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 bg-white hover:bg-gray-50 text-base">
                                取消
                            </button>
                            <button id="confirmOk" class="px-4 py-2 border border-transparent rounded-lg text-white bg-primary hover:bg-blue-700 text-base">
                                确定
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(confirmModal);
            
            document.getElementById('confirmCancel').onclick = () => {
                document.body.removeChild(confirmModal);
                resolve(false);
            };
            
            document.getElementById('confirmOk').onclick = () => {
                document.body.removeChild(confirmModal);
                resolve(true);
            };
        } else {
            // 桌面端使用原生确认框
            resolve(window.confirm(message));
        }
    });
}

/**
 * 显示提示对话框（移动端友好）
 * @param {string} message - 提示消息
 */
function showAlert(message) {
    // 检查是否在移动端
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // 移动端使用自定义提示弹窗
        const alertModal = document.createElement('div');
        alertModal.className = 'fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4';
        alertModal.id = 'mobileAlertModal';
        
        alertModal.innerHTML = `
            <div class="bg-white rounded-xl w-full max-w-md p-6">
                <div class="text-center">
                    <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
                        <i class="fa fa-info-circle text-blue-600 text-xl"></i>
                    </div>
                    <h3 class="mt-4 text-lg font-medium text-gray-800">提示</h3>
                    <p class="mt-2 text-gray-600">${message}</p>
                    <div class="mt-6">
                        <button id="alertOk" class="px-4 py-2 border border-transparent rounded-lg text-white bg-primary hover:bg-blue-700 w-full text-base">
                            确定
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(alertModal);
        
        document.getElementById('alertOk').onclick = () => {
            document.body.removeChild(alertModal);
        };
    } else {
        // 桌面端使用原生提示框
        window.alert(message);
    }
}

/**
 * 日期格式化函数
 * @param {Date|string} date - 日期对象或日期字符串
 * @returns {string} 格式化的日期字符串 (YYYY-MM-DD)
 */
function formatDate(date) {
    if (!date) return '';
    
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
}

/**
 * 日期时间格式化函数
 * @param {Date|string} date - 日期对象或日期字符串
 * @returns {string} 格式化的日期时间字符串 (YYYY-MM-DD HH:mm:ss)
 */
function formatDateTime(date) {
    if (!date) return '';
    
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

/**
 * 金额格式化函数
 * @param {number} amount - 金额
 * @param {number} decimals - 小数位数
 * @returns {string} 格式化的金额字符串
 */
function formatCurrency(amount, decimals = 2) {
    if (amount === null || amount === undefined) return '';
    
    return parseFloat(amount).toFixed(decimals);
}

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {number} limit - 限制时间（毫秒）
 * @returns {Function} 节流后的函数
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * 格式化日期显示
 * @param {string} dateStr - 日期字符串
 * @returns {string} 格式化的日期显示字符串
 */
function formatDateDisplay(dateStr) {
    if (!dateStr) return '';
    try {
        // 尝试解析带时间的格式
        const dt = new Date(dateStr);
        const year = dt.getFullYear();
        const month = String(dt.getMonth() + 1).padStart(2, '0');
        const day = String(dt.getDate()).padStart(2, '0');
        const hours = String(dt.getHours()).padStart(2, '0');
        const minutes = String(dt.getMinutes()).padStart(2, '0');
        const seconds = String(dt.getSeconds()).padStart(2, '0');
        return `${year}年${month}月${day}日 ${hours}:${minutes}:${seconds}`;
    } catch (error) {
        return dateStr;
    }
}

/**
 * 移动端风格确认弹窗
 * @param {string} title - 弹窗标题
 * @param {string} message - 弹窗消息
 * @param {function} callback - 确认回调函数
 * @param {string} type - 弹窗类型 ('warning', 'danger')
 */
function showMobileConfirm(title, message, callback, type = 'warning') {
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmMessage').textContent = message;
    window.mobileConfirmCallback = callback;
    
    const iconContainer = document.querySelector('#mobileConfirmModal .rounded-full');
    const icon = iconContainer.querySelector('i');
    
    if (type === 'warning') {
        iconContainer.className = 'w-14 h-14 mx-auto mb-4 rounded-full bg-orange-100 flex items-center justify-center';
        icon.className = 'fa fa-question text-2xl text-orange-500';
    } else if (type === 'danger') {
        iconContainer.className = 'w-14 h-14 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center';
        icon.className = 'fa fa-exclamation text-2xl text-red-500';
    }
    
    document.getElementById('mobileConfirmModal').classList.remove('hidden');
}

/**
 * 关闭移动端确认弹窗
 */
function closeMobileConfirm() {
    document.getElementById('mobileConfirmModal').classList.add('hidden');
    window.mobileConfirmCallback = null;
}

/**
 * 执行移动端确认弹窗回调
 */
function executeMobileConfirm() {
    if (window.mobileConfirmCallback) {
        window.mobileConfirmCallback();
    }
    closeMobileConfirm();
}