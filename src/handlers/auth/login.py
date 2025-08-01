from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from states.auth_states import LoginStates

from api.client import BackendClient
from api.redis_client import get_user_tz

from keyboards.settings import settings_kb
from keyboards.tasks import get_my_tasks_kb


login_router = Router(name='Login')


@login_router.callback_query(F.data == 'login_start')
async def ask_email(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await cq.message.answer("Please send me your email")
    await state.set_state(LoginStates.waiting_email)


@login_router.message(LoginStates.waiting_email)
async def ask_password(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.delete()
    await message.answer("Now send me password for your tracker account")
    await state.set_state(LoginStates.waiting_password)


@login_router.message(LoginStates.waiting_password)
async def login(message: types.Message, state: FSMContext):
    client = BackendClient(message.from_user.username)
    email = (await state.get_data()).get('email')
    password = message.text
    await client.login(email, password)
    await message.delete()
    await state.clear()
    await get_user_tz(message.from_user.username)
    await message.answer('You are logged in!', reply_markup=get_my_tasks_kb())
