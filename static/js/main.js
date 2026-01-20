// SUPERPLAC 인플랩 - Main JavaScript

// 전역 변수
let products = [];
let platforms = [];
let selectedProduct = null;
let cart = [];

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    loadPlatforms();
    loadProducts();
    loadStats();
    initializeEventListeners();
});

// 플랫폼 로드
async function loadPlatforms() {
    try {
        const response = await fetch('/api/platforms');
        const data = await response.json();
        platforms = data.platforms;
        renderPlatforms();
        renderPlatformFilters();
    } catch (error) {
        console.error('플랫폼 로드 오류:', error);
    }
}

// 플랫폼 렌더링
function renderPlatforms() {
    const container = document.getElementById('platformsContainer');
    
    container.innerHTML = platforms.map(platform => `
        <div class="col-md-4 col-lg-2-4 fade-in-up">
            <div class="card platform-card" onclick="filterByPlatform('${platform.id}')">
                <div class="card-body text-center p-4">
                    <div class="platform-icon" style="background-color: ${platform.color}20; color: ${platform.color};">
                        <i class="${platform.icon}"></i>
                    </div>
                    <h5 class="card-title">${platform.name}</h5>
                    <p class="text-muted small">성장 서비스</p>
                </div>
            </div>
        </div>
    `).join('');
}

// 플랫폼 필터 렌더링
function renderPlatformFilters() {
    const filterContainer = document.getElementById('platformFilter');
    
    platforms.forEach(platform => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-outline-primary';
        btn.setAttribute('data-platform', platform.id);
        btn.innerHTML = `<i class="${platform.icon} me-1"></i> ${platform.name}`;
        btn.onclick = () => filterByPlatform(platform.id);
        filterContainer.appendChild(btn);
    });
}

// 상품 로드
async function loadProducts(platform = null) {
    try {
        const url = platform ? `/api/products?platform=${platform}` : '/api/products';
        const response = await fetch(url);
        products = await response.json();
        renderProducts();
    } catch (error) {
        console.error('상품 로드 오류:', error);
        showError('상품을 불러오는 중 오류가 발생했습니다.');
    }
}

// 상품 렌더링
function renderProducts() {
    const container = document.getElementById('productsContainer');
    
    if (products.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="fas fa-box-open fa-3x text-muted mb-3"></i>
                <p class="text-muted">상품이 없습니다.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = products.map(product => {
        const platformInfo = platforms.find(p => p.id === product.platform);
        const icon = platformInfo ? platformInfo.icon : 'fas fa-star';
        const color = platformInfo ? platformInfo.color : '#666';
        
        return `
            <div class="col-md-6 col-lg-4 fade-in-up">
                <div class="card product-card">
                    <div class="card-body p-4">
                        <div class="d-flex align-items-center mb-3">
                            <div class="platform-icon me-3" style="width: 50px; height: 50px; background-color: ${color}20; color: ${color}; font-size: 1.5rem;">
                                <i class="${icon}"></i>
                            </div>
                            <div>
                                <h5 class="card-title mb-0">${product.name}</h5>
                                <small class="text-muted">${platformInfo ? platformInfo.name : product.platform}</small>
                            </div>
                        </div>
                        
                        <p class="card-text text-muted mb-3">${product.description || '고품질 서비스 제공'}</p>
                        
                        <div class="product-details mb-3">
                            <div class="detail-item">
                                <i class="fas fa-clock"></i>
                                <span>배송: ${product.delivery_time || '1-3일'}</span>
                            </div>
                            <div class="detail-item">
                                <i class="fas fa-sort-amount-down"></i>
                                <span>최소: ${formatNumber(product.min_quantity)}개</span>
                            </div>
                            <div class="detail-item">
                                <i class="fas fa-sort-amount-up"></i>
                                <span>최대: ${formatNumber(product.max_quantity)}개</span>
                            </div>
                        </div>
                        
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <div class="price-tag">₩${formatNumber(product.base_price)}</div>
                                <div class="price-unit">개당 가격</div>
                            </div>
                            <button class="btn btn-primary" onclick="openOrderModal(${product.id})">
                                <i class="fas fa-shopping-cart me-2"></i>주문
                            </button>
                        </div>
                        
                        ${getDiscountBadge(product)}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// 할인 배지 생성
function getDiscountBadge(product) {
    if (product.min_quantity >= 1000) {
        return `
            <div class="mt-3">
                <span class="discount-badge">
                    <i class="fas fa-tag me-1"></i>대량 구매 시 최대 20% 할인
                </span>
            </div>
        `;
    }
    return '';
}

// 플랫폼별 필터링
function filterByPlatform(platform) {
    // 버튼 활성화 상태 변경
    document.querySelectorAll('#platformFilter .btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-platform') === platform) {
            btn.classList.add('active');
        }
    });
    
    // 상품 필터링
    if (platform === 'all') {
        loadProducts();
    } else {
        loadProducts(platform);
    }
    
    // 상품 섹션으로 스크롤
    document.getElementById('products').scrollIntoView({ behavior: 'smooth' });
}

// 통계 로드
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        animateCounter('statsProducts', stats.total_products);
        animateCounter('statsOrders', stats.completed_orders);
    } catch (error) {
        console.error('통계 로드 오류:', error);
    }
}

// 카운터 애니메이션
function animateCounter(elementId, target) {
    const element = document.getElementById(elementId);
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 30);
}

// 주문 모달 열기
async function openOrderModal(productId) {
    selectedProduct = products.find(p => p.id === productId);
    
    if (!selectedProduct) {
        showError('상품을 찾을 수 없습니다.');
        return;
    }
    
    // 모달 데이터 설정
    document.getElementById('productId').value = selectedProduct.id;
    document.getElementById('modalProductName').textContent = selectedProduct.name;
    document.getElementById('quantity').value = selectedProduct.min_quantity;
    document.getElementById('quantity').min = selectedProduct.min_quantity;
    document.getElementById('quantity').max = selectedProduct.max_quantity;
    document.getElementById('quantityHint').textContent = 
        `최소: ${formatNumber(selectedProduct.min_quantity)}개 / 최대: ${formatNumber(selectedProduct.max_quantity)}개`;
    
    // 초기 가격 계산
    calculateTotalPrice();
    
    // 모달 표시
    const modal = new bootstrap.Modal(document.getElementById('orderModal'));
    modal.show();
}

// 총 가격 계산
function calculateTotalPrice() {
    const quantity = parseInt(document.getElementById('quantity').value) || 0;
    
    if (!selectedProduct || quantity === 0) {
        document.getElementById('totalPrice').textContent = '₩0';
        return;
    }
    
    let unitPrice = selectedProduct.base_price;
    let discountRate = 0;
    
    // 수량별 할인
    if (quantity >= 10000) {
        discountRate = 0.2; // 20%
    } else if (quantity >= 5000) {
        discountRate = 0.15; // 15%
    } else if (quantity >= 1000) {
        discountRate = 0.1; // 10%
    }
    
    unitPrice *= (1 - discountRate);
    const totalPrice = unitPrice * quantity;
    
    let priceText = `₩${formatNumber(Math.round(totalPrice))}`;
    if (discountRate > 0) {
        priceText += ` <span class="text-success">(${discountRate * 100}% 할인 적용)</span>`;
    }
    
    document.getElementById('totalPrice').innerHTML = priceText;
}

// 주문 제출
async function submitOrder() {
    const form = document.getElementById('orderForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const orderData = {
        product_id: parseInt(document.getElementById('productId').value),
        customer_name: document.getElementById('customerName').value,
        customer_email: document.getElementById('customerEmail').value,
        target_url: document.getElementById('targetUrl').value,
        quantity: parseInt(document.getElementById('quantity').value),
        notes: document.getElementById('notes').value
    };
    
    try {
        // 주문 생성
        const orderResponse = await fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        
        if (!orderResponse.ok) {
            const error = await orderResponse.json();
            throw new Error(error.detail || '주문 생성 실패');
        }
        
        const order = await orderResponse.json();
        
        // 결제 생성
        const paymentData = {
            order_id: order.id,
            method: document.getElementById('paymentMethod').value
        };
        
        const paymentResponse = await fetch('/api/payments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(paymentData)
        });
        
        if (!paymentResponse.ok) {
            throw new Error('결제 처리 실패');
        }
        
        const payment = await paymentResponse.json();
        
        // 성공 메시지
        showSuccess(`주문이 완료되었습니다! 주문번호: ${order.id}`);
        
        // 모달 닫기
        const modal = bootstrap.Modal.getInstance(document.getElementById('orderModal'));
        modal.hide();
        
        // 폼 초기화
        form.reset();
        
    } catch (error) {
        console.error('주문 오류:', error);
        showError(error.message || '주문 처리 중 오류가 발생했습니다.');
    }
}

// 이벤트 리스너 초기화
function initializeEventListeners() {
    // 수량 변경 시 가격 재계산
    document.getElementById('quantity').addEventListener('input', calculateTotalPrice);
    
    // 주문 제출 버튼
    document.getElementById('submitOrder').addEventListener('click', submitOrder);
}

// 유틸리티 함수
function formatNumber(num) {
    return new Intl.NumberFormat('ko-KR').format(num);
}

function showSuccess(message) {
    alert('✅ ' + message);
}

function showError(message) {
    alert('❌ ' + message);
}

// 부드러운 스크롤
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
