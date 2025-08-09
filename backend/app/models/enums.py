import enum


class CandidateStage(str, enum.Enum):
    NEW = "Новый"
    CONTACT = "Контакт установлен"
    WAIT_DOCS = "Ожидаем документы"
    DOCS_OK = "Документы получены"
    PERMIT_ORDERED = "Заказ разрешения"
    VISA_FLOW = "Виза"
    RED_PAPER = "Красная бумага"
    READY_TO_GO = "Готов к выезду"
    PLAN_ARRIVAL = "Планируем приезд"
    AT_BASE = "На базе клиента"
    HIRED = "Трудоустроен"
    REJECTED = "Отклонён"
