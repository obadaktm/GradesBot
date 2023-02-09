import os

import Subjetcs

TOKEN = os.environ.get("TOKEN")
subjects = Subjetcs.Subjects(TOKEN)

dp = subjects.updater.dispatcher
dp.add_handler(subjects.startCommand)
dp.add_handler(subjects.registerCommand)
dp.add_handler(subjects.aboutCommand)
dp.add_handler(subjects.howToUseCommand)
dp.add_handler(subjects.setAllSubjectMarksConversation)
dp.add_handler(subjects.getAllSubjectMarksCommand)
dp.add_handler(subjects.changeSubjectNameConversation)
dp.add_handler(subjects.changeYearMarkConversation)
dp.add_handler(subjects.changePaperMarkConversation)
dp.add_handler(subjects.sendMessageCommand)
dp.add_handler(subjects.receivedMessage)
dp.add_handler(subjects.receivedSticker)

subjects.updater.start_polling()
