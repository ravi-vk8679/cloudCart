import streamlit as st
from pathlib import Path
import requests
from html import escape

backend_url = "http://localhost:8000"


st.set_page_config(
    page_title="Cloud Cart",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

## Get the CSS file path and read its content

css_path = Path(__file__).parent / "style.css"

st.markdown(
    f"<style>{css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

def notify(message: str) -> None:
    st.session_state["notification"] = message

## Add Product to an Inventory
def show_add_product():
    with st.container(key="add_product_card"):
        st.markdown('<h2 class="card-title">Add Product</h2>', unsafe_allow_html=True)
        with st.form("add_product_form", clear_on_submit=True, border=False):
            id_col, name_col, desc_col, price_col = st.columns(4, gap="small")
            with id_col:
                product_id = st.text_input("ID", placeholder="ID", label_visibility="collapsed", max_chars=12)
            with name_col:
                name = st.text_input("Name", placeholder="Name", label_visibility="collapsed", max_chars=120)
            with desc_col:
                description = st.text_input("Description", placeholder="Description", label_visibility="collapsed", max_chars=2000)
            with price_col:
                price = st.text_input("Price", placeholder="Price", label_visibility="collapsed")
            quantity_col, filler = st.columns([1, 3], gap="small")
            with quantity_col:
                quantity = st.text_input("Quantity", placeholder="Quantity", label_visibility="collapsed")
            submitted = st.form_submit_button("Add", type="primary")

            if submitted:
                try:
                    response = requests.post(f"{backend_url}/product", json={
                        "id": int(product_id),
                        "name": name,
                        "description": description,
                        "price": float(price),
                        "quantity": int(quantity)
                    })

                    print(response.status_code, response.text)

                    if response.status_code == 200:
                        st.info(f"Added {name} successfully.")
                        # notify(f"Added {name} successfully.")
                        st.rerun()
                    else:
                        st.error(f"Error adding product: {response.text}")

                except requests.RequestException:
                    st.html(
                        """
                        <div style="background-color: #6a1b9a; padding: 15px; border-radius: 5px; color: white; border-left: 5px solid #4a148c;">
                            <strong>Error:</strong> Could not connect to backend. Check if the backend is running.
                        </div>
                        """
                    )
                    st.stop()

                # except:
                #     st.error("Could not connect to backend. Please check if the backend is running.")

#Show Products Table
                    
def show_product_table(products: list[dict]) -> None:
    with st.container(key="products_card"):
        st.markdown('<h2 class="card-title products-heading">Products</h2>', unsafe_allow_html=True)
        if not products:
            st.info("No products found. Try changing your search or adding an item.")
            return

        weights = [0.55, 1.14, 1.55, 1.0, 0.92, 1.55]
        titles = ["ID ↑", "NAME", "DESCRIPTION", "PRICE", "QUANTITY", "ACTIONS"]
        columns = st.columns(weights, gap="small", vertical_alignment="center")
        for column, title in zip(columns, titles):
            with column:
                st.markdown(f'<div class="table-th">{escape(title)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="table-divider table-header-divider"></div>', unsafe_allow_html=True)

        for product in products:
            columns = st.columns(weights, gap="small", vertical_alignment="center")
            with columns[0]:
                st.markdown(f'<div class="row-id">{product["id"]}</div>', unsafe_allow_html=True)
            with columns[1]:
                st.markdown(f'<div class="row-name" title="{escape(product["name"], quote=True)}">{escape(product["name"])}</div>', unsafe_allow_html=True)
            with columns[2]:
                description = product["description"] or "—"
                st.markdown(f'<div class="row-description" title="{escape(description, quote=True)}">{escape(description)}</div>', unsafe_allow_html=True)
            with columns[3]:
                st.markdown(f'<div class="row-price">${product["price"]:,.2f}</div>', unsafe_allow_html=True)
            with columns[4]:
                st.markdown(f'<span class="quantity-pill">{product["quantity"]}</span>', unsafe_allow_html=True)
            with columns[5]:
                edit_col, delete_col = st.columns(2, gap="small")
                with edit_col:
                    if st.button("Edit", key=f"edit_{product['id']}", use_container_width=True):
                        edit_model(product)
                with delete_col:
                    if st.button("Delete", key=f"delete_{product['id']}", use_container_width=True):
                        delete_model(product)
            st.markdown('<div class="table-divider"></div>', unsafe_allow_html=True)


## Edit Product Form
@st.dialog("Edit product")
def edit_model(product: dict) -> None:
    st.caption(f"Product ID: {product['id']}")
    with st.form(f"edit_form_{product['id']}"):
        name = st.text_input("Product name", value=product["name"])
        description = st.text_area("Description", value=product["description"])
        price = st.text_input("Price ($)", value=f"{product['price']:.2f}")
        quantity = st.number_input("Quantity", min_value=0, step=1, value=product["quantity"])
        save = st.form_submit_button("Save changes", type="primary", use_container_width=True)

        if save:
            try:
                response = requests.put(f"{backend_url}/product/{product['id']}", json={
                        "id": product['id'],
                        "name": name,
                        "description": description,
                        "price": price,
                        "quantity": quantity
                    })
                print(response.status_code, response.text)
                if response.status_code == 200:
                    st.info(f"Updated {product['name']} successfully.")
                    st.rerun()
                else:
                    st.error(f"Error Updating product: {response.text}")
            except requests.RequestException:
                st.html(
                    """
                    <div style="background-color: #6a1b9a; padding: 15px; border-radius: 5px; color: white; border-left: 5px solid #4a148c;">
                        <strong>Error:</strong> Could not connect to backend. Check if the backend is running.
                    </div>
                    """
                )
                st.stop()

## Remove product from Inventory
@st.dialog("Delete product?")
def delete_model(product: dict) -> None:
    try:
        response = requests.delete(f"{backend_url}/product", params={"id": product["id"]})
        if response.status_code == 200:
            st.info(f"Deleted {product['name']} successfully.")
            st.rerun()
        else:
            st.error(f"Error deleting product: {response.text}")
    except requests.RequestException:
        st.html(
            """
            <div style="background-color: #6a1b9a; padding: 15px; border-radius: 5px; color: white; border-left: 5px solid #4a148c;">
                <strong>Error:</strong> Could not connect to backend. Check if the backend is running.
            </div>
            """
        )
        st.stop()

# -- Header ------------------------------------------------------------------
brand, header_action = st.columns([12, 1], vertical_alignment="center")
with brand:
    st.markdown(
        '<div class="brand"><span class="brand-icon">☁️🛒</span><span>Cloud Cart</span></div>',
        unsafe_allow_html=True,
    )
with header_action:
    with st.container(key="refresh_button"):
        if st.button("Refresh", use_container_width=True):
            st.rerun()

st.markdown('<div class="header-spacer"></div>', unsafe_allow_html=True)

# -- Centered dashboard ------------------------------------------------------
side_left, content, side_right = st.columns([1, 9, 1], gap="small")
with content:
    left_panel, right_panel = st.columns([2.86, 1.5], gap="large", vertical_alignment="top")

    with right_panel:
        with st.container(key="search_bar"):
            query = st.text_input(
                "Search products", placeholder="Search by id, name or description...",
                label_visibility="collapsed", key="product_search",
            )

        with st.container(key="promo_card"):
            st.markdown(
                '''<div class="promo-content">
                  <div class="promo-title"><span class="promo-square"></span>Track. Manage. Grow.</div>
                  <p>Streamline your inventory with smart product<br class="promo-break"/>
                  management that scales with your business.</p>
                  <div class="powered-by">POWERED BY&nbsp; <strong>RAVI CLOUD</strong></div>
                </div>''',
                unsafe_allow_html=True,
            )

    with left_panel:
        try:
            response = requests.get(f"{backend_url}/products/count")
            print(response)
            data = response.json()
            total = data.get("total_products", 0) 
            print(total)
        except requests.RequestException:
            st.html(
                """
                <div style="background-color: #6a1b9a; padding: 15px; border-radius: 5px; color: white; border-left: 5px solid #4a148c;">
                    <strong>Error:</strong> Could not load PRODUCT COUNT from backend. Check if the backend is running.
                </div>
                """
            )
            st.stop()

        st.markdown(
            f'<div class="count-pill">Total Item Types: <span style="color: #FF0000; font-weight: bold;">{total}</span></div>', 
            unsafe_allow_html=True
        )

        ## Add Product Form
        show_add_product()

        ## Show Products list

        try:
            response = requests.get(f"{backend_url}/products")
            products = response.json()
            show_product_table(products)
        except requests.RequestException:
            st.html(
                """
                <div style="background-color: #6a1b9a; padding: 15px; border-radius: 5px; color: white; border-left: 5px solid #4a148c;">
                    <strong>Error:</strong> Could not load PRODUCTS from backend. Check if the backend is running.
                </div>
                """
            )
            st.stop()

        # if query:
        #     st.markdown(
        #         f'<div class="results-count">Showing {len(products)} matching product(s).</div>',
        #         unsafe_allow_html=True,
        #     )