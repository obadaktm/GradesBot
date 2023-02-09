import pandas as pd
from csv2pdf import convert
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.update import Update

from Init import Init


class Subjects(Init):
    def __init__(self, TOKEN):
        super().__init__(TOKEN)
        self.year, self.subject, self.yearMarks, self.finalMark = range(4)
        self.marksDataFrame = pd.read_csv("Marks.csv", dtype={'User_id': 'Int64', 'Chat_id': 'Int64', 'Year': 'Int64',
                                                              'YearMarks': 'Int64',
                                                              'PaperMarks': 'Int64',
                                                              'FinalMark': 'Int64'})
        try:
            self.MarkRow = self.marksDataFrame["User_id"].values[-1] + 1
        except IndexError:
            self.MarkRow = 1
        self.subjectName = ""
        self.oldSubject = ""
        self.newSubject = ""
        self.x = ["Year", "Subject", "YearMarks", "PaperMarks", "FinalMark"]
        self.setAllSubjectMarksConversation = ConversationHandler(
            entry_points=[CommandHandler('add_subject_marks', self.addAllMarks, self.filtr)],
            states={
                self.year: [MessageHandler(self.filtr, self.setYear)],
                self.subject: [MessageHandler(self.filtr, self.setSubject)],
                self.yearMarks: [MessageHandler(self.filtr, self.setYearMarks)],
                self.finalMark: [MessageHandler(self.filtr, self.setPaperMark)]
            },
            fallbacks=[]
        )
        self.getAllSubjectMarksCommand = CommandHandler('get_all_marks', self.getAllMarks, self.filtr)
        self.message, self.markChanger = range(2)
        self.changeYearMarkConversation = ConversationHandler(
            entry_points=[CommandHandler('change_year_mark', self.changeYearMark, self.filtr)],
            states={
                self.message: [MessageHandler(self.filtr, self.yearMarkChanger)],
                self.markChanger: [MessageHandler(self.filtr, self.yearMarkHandler)]
            },
            fallbacks=[]
        )
        self.papermark, self.papermarkhandler = range(2)
        self.changePaperMarkConversation = ConversationHandler(
            entry_points=[CommandHandler('change_paper_mark', self.changePaperMark, self.filtr)],
            states={
                self.papermark: [MessageHandler(self.filtr, self.paperMarkChanger)],
                self.papermarkhandler: [MessageHandler(self.filtr, self.paperMarkHandler)]
            },
            fallbacks=[]
        )
        self.oldSubjectName, self.newSubjectName = range(2)
        self.changeSubjectNameConversation = ConversationHandler(
            entry_points=[CommandHandler('change_subject_name', self.changeSubjectName, self.filtr)],
            states={
                self.oldSubjectName: [MessageHandler(self.filtr, self.oldName)],
                self.newSubjectName: [MessageHandler(self.filtr, self.newName)]
            },
            fallbacks=[]
        )

    def storeMarkInformation(self, update: Update, context: CallbackContext, field, row):
        if self.checkSubject(self.marksDataFrame, row, field, update, context):
            self.marksDataFrame.to_csv("Marks.csv", index=False)
            return True
        else:
            return False

    def checkSubject(self, dataframe, row, field, update: Update, context: CallbackContext):
        found = False
        if field == "Subject":
            marksDataFrame = pd.read_csv("Marks.csv", dtype={'User_id': 'Int64', 'Chat_id': 'Int64',
                                                             'Year': 'Int64',
                                                             'YearMarks': 'Int64',
                                                             'PaperMarks': 'Int64',
                                                             'FinalMark': 'Int64'})
            temp = marksDataFrame.loc[marksDataFrame["Chat_id"] == int(update.message.chat_id)]
            if temp["Subject"].isin([f"{update.message.text}".lower()]).any().any():
                found = True
            if found:
                self.bot.send_message(chat_id=update.message.chat_id,
                                      text="This Subject is already exist.\nEnter another subject:\nهذه المادة مسجلة مسبقا \n:أدخل مادة أخرى")
                marksDataFrame.to_csv("Marks.csv", index=False)
                return False
            else:
                dataframe.loc[row, "Subject"] = f"{update.message.text}".lower()
                return True
        else:
            dataframe.loc[row, f"{field}"] = int(update.message.text)
            dataframe.loc[row, "Chat_id"] = update.message.chat_id
            dataframe.loc[row, "User_id"] = self.MarkRow
            if field == "PaperMarks":
                dataframe.loc[row, "FinalMark"] = int(
                    dataframe.loc[row, "YearMarks"] + dataframe.loc[row, "PaperMarks"])
            return True

    def addAllMarks(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="Send the year number you need that subject belongs to\nادخل رقم السنة التي تتبع لها المادة التي تريد إدخالها")
        return self.year

    def setYear(self, update: Update, context: CallbackContext):
        try:
            self.storeMarkInformation(update, context, "Year", self.MarkRow)
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="Enter the name of the subject in English\nأدخل اسم المادة باللغة الإنكليزية")
            return self.subject
        except:
            return ConversationHandler.END

    def setSubject(self, update: Update, context: CallbackContext):
        if self.storeMarkInformation(update, context, "Subject", self.MarkRow):
            pass
        else:
            return self.subject
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="Enter the Year marks of the subject\nأدخل علامة العملي كاملة")
        return self.yearMarks

    def setYearMarks(self, update: Update, context: CallbackContext):
        try:
            self.storeMarkInformation(update, context, "YearMarks", self.MarkRow)
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="Enter the on paper marks of the subject\nأدخل علامة النظري دون علامة العملي ")
            return self.finalMark
        except:
            return ConversationHandler.END

    def setPaperMark(self, update: Update, context: CallbackContext):
        try:
            self.storeMarkInformation(update, context, "PaperMarks", self.MarkRow)
            self.MarkRow += 1
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="Your subject marks are saved.\nYou can call them any time you want using thin command /get_all_marks\nتم حفظ العلامات\nيمكنك طلبهم في اي وقت تريد باستخدام الأمر /get_all_marks")
            return ConversationHandler.END
        except:
            return ConversationHandler.END

    def getAllMarks(self, update: Update, context: CallbackContext):
        j = 0
        marksDataFrame = pd.read_csv("Marks.csv", dtype={'User_id': 'Int64', 'Chat_id': 'Int64', 'Year': 'Int64',
                                                         'YearMarks': 'Int64',
                                                         'PaperMarks': 'Int64',
                                                         'FinalMark': 'Int64'})
        temp = pd.read_csv('temp.csv', dtype={'Year': 'Int64',
                                              'Subject': 'string',
                                              'YearMarks': 'Int64',
                                              'PaperMarks': 'Int64',
                                              'FinalMark': 'Int64'})
        for i in range(len(marksDataFrame.index)):
            if marksDataFrame["Chat_id"][i] == int(update.message.chat_id):
                for field in self.x:
                    temp.loc[j, field] = marksDataFrame[field][i]
                j += 1
        temp = temp.sort_values("Year")
        temp = temp[self.x]
        temp.to_csv("temp.csv", index=False)
        marksDataFrame.to_csv("Marks.csv", index=False)
        convert("temp.csv", "Marks.pdf", font="Font/IBMPlexSansArabic-Regular.ttf")
        temp.drop(temp.index, inplace=True)
        temp.to_csv("temp.csv", index=False)
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="please wait a second while processing the marks\nرجاء انتظر لبضع ثواني لمعالجة العلامات ")
        self.bot.send_document(chat_id=update.message.chat_id, document=open('Marks.pdf', 'rb'))

    def changeYearMark(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="please enter the name of the subject that you need to change it's year mark\nأدخل اسم المادة التي تريد تعديل علامة العملي فيها")
        return self.message

    def yearMarkChanger(self, update: Update, context: CallbackContext):
        self.subjectName = f"{update.message.text}".lower()
        marksDataFrame = pd.read_csv("Marks.csv", dtype={'User_id': 'Int64', 'Chat_id': 'Int64',
                                                         'Year': 'Int64',
                                                         'YearMarks': 'Int64',
                                                         'PaperMarks': 'Int64',
                                                         'FinalMark': 'Int64'})
        temp = marksDataFrame.loc[marksDataFrame["Chat_id"] == int(update.message.chat_id)]
        if temp["Subject"].isin([self.subjectName]).any().any():
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="Enter the new year mark\nأدخل علامة العملي الجديدة")
            return self.markChanger
        else:
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="This subject name not stored enter it by using this command /add_Subject_Marks \nاسم المادة غير مخزن قم بإدخال اسم المادة و علاماتها باستخدام الأمر /add_Subject_Marks")
            return ConversationHandler.END

    def yearMarkHandler(self, update: Update, context: CallbackContext):
        try:
            marksDataFrame = pd.read_csv("Marks.csv", dtype={'User_id': 'Int64', 'Chat_id': 'Int64', 'Year': 'Int64',
                                                             'YearMarks': 'Int64',
                                                             'PaperMarks': 'Int64',
                                                             'FinalMark': 'Int64'})
            for i in range(len(marksDataFrame)):
                if marksDataFrame["Chat_id"][i] == update.message.chat_id:
                    if marksDataFrame["Subject"][i] == self.subjectName:
                        marksDataFrame.loc[i, "YearMarks"] = int(update.message.text)
                        try:
                            marksDataFrame.loc[i, "FinalMark"] = int(
                                marksDataFrame["YearMarks"][i] + marksDataFrame["PaperMarks"][i])
                            marksDataFrame.to_csv("Marks.csv", index=False)
                            self.bot.send_message(chat_id=update.message.chat_id,
                                                  text=f"Year mark changed for {self.subjectName}\nتم تعديل علامة العملي لمادة {self.subjectName}")
                            return ConversationHandler.END
                        except:
                            return ConversationHandler.END
        except:
            return ConversationHandler.END

    def changePaperMark(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="please enter the name of the subject that you need to change it's paper mark\nأدخل اسم المادة التي تريد تعديل علامة النظري فيها")
        return self.papermark

    def paperMarkChanger(self, update: Update, context: CallbackContext):
        self.subjectName = f"{update.message.text}".lower()
        marksDataFrame = pd.read_csv("Marks.csv", dtype={'User_id': 'Int64', 'Chat_id': 'Int64',
                                                         'Year': 'Int64',
                                                         'YearMarks': 'Int64',
                                                         'PaperMarks': 'Int64',
                                                         'FinalMark': 'Int64'})
        temp = marksDataFrame.loc[marksDataFrame["Chat_id"] == int(update.message.chat_id)]
        if temp["Subject"].isin([self.subjectName]).any().any():
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="Enter the new paper mark without the year mark\nأدخل علامة النظري الجديدة دون علامة العملي")
            return self.papermarkhandler
        else:
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="This subject name not stored enter it by using this command /add_Subject_Marks \nاسم المادة غير مخزن قم بإدخال اسم المادة و علاماتها باستخدام الأمر /add_Subject_Marks")
            return ConversationHandler.END

    def paperMarkHandler(self, update: Update, context: CallbackContext):
        try:
            marksDataFrame = pd.read_csv("Marks.csv", dtype={'User_id': 'Int64', 'Chat_id': 'Int64', 'Year': 'Int64',
                                                             'YearMarks': 'Int64',
                                                             'PaperMarks': 'Int64',
                                                             'FinalMark': 'Int64'})
            for i in range(len(marksDataFrame)):
                if marksDataFrame["Chat_id"][i] == update.message.chat_id:
                    if marksDataFrame["Subject"][i] == self.subjectName:
                        marksDataFrame.loc[i, "PaperMarks"] = int(update.message.text)
                        try:
                            marksDataFrame.loc[i, "FinalMark"] = int(
                                marksDataFrame["YearMarks"][i] + marksDataFrame["PaperMarks"][i])
                            marksDataFrame.to_csv("Marks.csv", index=False)
                            self.bot.send_message(chat_id=update.message.chat_id,
                                                  text=f"Paper mark changed for {self.subjectName}\nتم تعديل علامة النظري لمادة {self.subjectName}")
                            return ConversationHandler.END
                        except:
                            return ConversationHandler.END
        except:
            return ConversationHandler.END

    def changeSubjectName(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="please enter the old subject name \nأدخل اسم المادة القديم")
        return self.oldSubjectName

    def oldName(self, update: Update, context: CallbackContext):
        found = False
        marksDataFrame = pd.read_csv("Marks.csv", dtype={'User_id': 'Int64', 'Chat_id': 'Int64',
                                                         'Year': 'Int64',
                                                         'YearMarks': 'Int64',
                                                         'PaperMarks': 'Int64',
                                                         'FinalMark': 'Int64'})
        self.oldSubject = f"{update.message.text}".lower()
        temp = marksDataFrame.loc[marksDataFrame["Chat_id"] == int(update.message.chat_id)]
        if temp["Subject"].isin([self.oldSubject]).any().any():
            found = True
        if found:
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="Enter the new subjetc name\nأدخل اسم المادة الجديد")
            marksDataFrame.to_csv("Marks.csv", index=False)
            return self.newSubjectName
        else:
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="This subject name not stored enter it by using this command /add_Subject_Marks \nاسم المادة غير مخزن قم بإدخال اسم المادة و علاماتها باستخدام الأمر /add_Subject_Marks")
            marksDataFrame.to_csv("Marks.csv", index=False)
            return ConversationHandler.END

    def newName(self, update: Update, context: CallbackContext):
        try:
            self.newSubject = f"{update.message.text}".lower()
            marksDataFrame = pd.read_csv("Marks.csv", dtype={'User_id': 'Int64', 'Chat_id': 'Int64',
                                                             'Year': 'Int64',
                                                             'YearMarks': 'Int64',
                                                             'PaperMarks': 'Int64',
                                                             'FinalMark': 'Int64'})
            temp = marksDataFrame.loc[marksDataFrame["Chat_id"] == int(update.message.chat_id)]
            if not temp["Subject"].isin([self.newSubject]).any().any():
                row = temp[temp["Subject"] == self.oldSubject].index.to_list()
                marksDataFrame.loc[row[0], "Subject"] = self.newSubject
                marksDataFrame.to_csv("Marks.csv", index=False)
                self.bot.send_message(chat_id=update.message.chat_id,
                                      text=f"Subject name changed from {self.oldSubject} to {self.newSubject}\nتم تعديل اسم المادة من {self.oldSubject} الى {self.newSubject}")
            else:
                marksDataFrame.to_csv("Marks.csv", index=False)
                self.bot.send_message(chat_id=update.message.chat_id,
                                      text="This Subject is already exist.\nEnter another subject:\nهذه المادة مسجلة مسبقا \n:أدخل مادة أخرى")
                return self.newSubjectName
            return ConversationHandler.END
        except:
            return ConversationHandler.END
