from django.contrib import admin
from django.contrib import messages

from .models import (
    CustomerProfile,
    BankAccount,
    Transaction,
    Card,
    Loan,
    SupportTicket,
    Notification,
)


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "customer_id",
        "user",
        "phone",
        "kyc_verified",
        "created_at",
    )
    search_fields = (
        "customer_id",
        "user__username",
        "user__email",
        "phone",
    )
    list_filter = ("kyc_verified",)


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        "account_number",
        "user",
        "account_type",
        "balance",
        "minimum_balance",
        "status",
        "created_at",
    )
    search_fields = (
        "account_number",
        "user__username",
        "user__email",
    )
    list_filter = ("account_type", "status")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "user",
        "account",
        "card",
        "transaction_type",
        "amount",
        "balance_after",
        "status",
        "created_at",
    )
    search_fields = (
        "reference",
        "user__username",
        "account__account_number",
        "description",
    )
    list_filter = ("transaction_type", "status", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        "masked_card",
        "user",
        "account",
        "card_type",
        "status",
        "expiry_date",
        "created_at",
    )
    search_fields = (
        "card_number",
        "user__username",
        "account__account_number",
    )
    list_filter = ("card_type", "status")

    @admin.display(description="Card Number")
    def masked_card(self, obj):
        return obj.masked_number()


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "account",
        "loan_type",
        "amount",
        "salary",
        "outstanding_amount",
        "status",
        "applied_at",
    )
    search_fields = (
        "user__username",
        "account__account_number",
    )
    list_filter = ("loan_type", "status")
    actions = ["approve_eligible_loans", "reject_selected_loans"]

    @admin.action(description="Approve selected eligible loans")
    def approve_eligible_loans(self, request, queryset):
        approved = 0
        skipped = 0
        for loan in queryset.filter(status="PENDING"):
            if loan.amount <= loan.salary:
                loan.status = "APPROVED"
                loan.outstanding_amount = loan.amount
                loan.save(update_fields=["status", "outstanding_amount"])
                Notification.objects.create(
                    user=loan.user,
                    title="Loan Approved",
                    message=f"Your loan of ₹{loan.amount:.2f} has been approved by the bank administrator.",
                )
                approved += 1
            else:
                skipped += 1
        if approved:
            self.message_user(request, f"{approved} eligible loan(s) approved.", messages.SUCCESS)
        if skipped:
            self.message_user(
                request,
                f"{skipped} loan(s) were not approved because the loan amount is greater than the applicant's salary.",
                messages.WARNING,
            )

    @admin.action(description="Reject selected pending loans")
    def reject_selected_loans(self, request, queryset):
        pending = queryset.filter(status="PENDING")
        count = pending.count()
        pending.update(status="REJECTED")
        for loan in pending:
            Notification.objects.create(
                user=loan.user,
                title="Loan Rejected",
                message="Your loan application was rejected by the bank administrator.",
            )
        self.message_user(request, f"{count} pending loan(s) rejected.", messages.SUCCESS)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_number",
        "user",
        "category",
        "subject",
        "status",
        "created_at",
    )
    search_fields = (
        "ticket_number",
        "user__username",
        "subject",
    )
    list_filter = ("category", "status")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "is_read",
        "created_at",
    )
    search_fields = (
        "user__username",
        "title",
        "message",
    )
    list_filter = ("is_read", "created_at")


admin.site.site_header = "Finova Bank Administration"
admin.site.site_title = "Finova Bank Admin"
admin.site.index_title = "Bank Management"
