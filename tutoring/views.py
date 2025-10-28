from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TutoringRoom, Message
from .ai_quiz_generator import generate_answer
from django.contrib import messages


@login_required
def tutoring_home(request):
    rooms = TutoringRoom.objects.all()
    return render(request, "tutoring_home.html", {"rooms": rooms})


@login_required
def create_tutoring_room(request):
    if request.method == "POST":
        name = request.POST.get("name")
        subject = request.POST.get("subject")
        TutoringRoom.objects.create(
            name=name,
            subject=subject,
            created_by=request.user
        )
        return redirect("tutoring_home")
    return render(request, "create_tutoring_room.html")


@login_required
def tutoring_room(request, room_id):
    room = get_object_or_404(TutoringRoom, id=room_id)

    if request.method == "POST":
        question = request.POST.get("question")
        if question:
            ai_response = generate_answer(question)
            Message.objects.create(
                room=room,
                user=request.user,
                question=question,
                ai_response=ai_response
            )
            return redirect("tutoring_room", room_id=room.id)  # Refresh page

    messages = room.messages.all().order_by("created_at")
    return render(request, "tutoring_room.html", {"room": room, "messages": messages})

@login_required
def delete_tutoring_room(request, room_id):
    room = get_object_or_404(TutoringRoom, id=room_id)

    # Only the creator can delete
    # if room.created_by != request.user:
    #     messages.error(request, "You are not allowed to delete this room.")
    #     return redirect("tutoring_home")

    if request.method == "POST":
        room.delete()
        messages.success(request, f"Room '{room.name}' has been deleted.")
        return redirect("tutoring_home")

    # For safety, confirm before deleting
    return render(request, "tutoring/confirm_delete.html", {"room": room})


