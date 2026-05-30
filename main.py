import os
from datetime import date
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from models.expenses import Expense


app = FastAPI()
templates = Jinja2Templates(directory="templates")


class ExpenseCreate(BaseModel):
    id: int
    amount: float
    category: str
    date: date
    description: str


expenses: List[Expense] = []


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "initial_total": sum(expense.amount for expense in expenses),
            "initial_count": len(expenses),
        },
    )


@app.get("/expenses")
def list_expenses():
    return expenses


@app.post("/expenses", status_code=201)
def create_expense(expense: ExpenseCreate):
    if any(existing.id == expense.id for existing in expenses):
        raise HTTPException(status_code=409, detail="Expense with this ID already exists")

    new_expense = Expense(**expense.model_dump())
    expenses.append(new_expense)
    return new_expense


@app.get("/expenses/total")
def get_total_expenses():
    return {"total_expenses": round(sum(expense.amount for expense in expenses), 2)}


@app.get("/expense/{expense_id}", response_class=HTMLResponse)
def get_expense_detail(request: Request, expense_id: int):
    expense = next((item for item in expenses if item.id == expense_id), None)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    return templates.TemplateResponse(
        "expense_details.html",
        {
            "request": request,
            "expense": expense,
        },
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
