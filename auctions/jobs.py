from .models import Auction
from datetime import datetime
import requests


def resolve_auction_job():
    timestamp = str(datetime.now())
    print("[%s] Starting resolve job..." % timestamp)
    due_auctions = Auction.objects.get_all_due()
    for auction in due_auctions:
        if auction.get_latest_bidder() is not None:
            print("Resolving auction %s" % auction.title)

            title = auction.title
            seller = auction.seller
            winner = auction.get_latest_bidder()
            winning_bid = auction.get_latest_bid_amount()

            seller_subject = "Your auction %s has been resolved" % title
            seller_body = "Congratulations, your auction has been resolved!\n\nThe winner is %s, with a bid of %d €" % winner, winning_bid

            winner_subject = "You have won the auction %s" % title
            winner_body = "Congratulations, you have won the auction %s with your bid of %d" % title, winning_bid

            loser_subject = "The Auction %s has been resolved." % title
            loser_body = "Unfortunately, the auction %s that you bid on was won by someone else." % title

            losers = Auction.objects.get_losers()

            for loser in losers:
                loser.email_user(loser_subject, loser_body)
            seller.email_user(seller_subject, seller_body)
            winner.email_user(winner_subject, winner_body)

        # The auction has no bids
        else:
            print("Due action %s had no bids" % auction.title)
            seller = auction.seller
            title = auction.title
            subject = "Your auction %s ended with no bids." % title
            body = "Unfortunately, your auction %s did not get any bids, and has now expired." % title
            seller.email_user(subject, body)






